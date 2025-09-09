import os
import base64
import click
import lxml.etree as ET


default_session_duration = 3600


def extract(html):
    assertion = None

    # Check to see if login returned an error
    # Since we're screen-scraping the login form, we need to pull it out of a label
    errors = html.findall('.//form[@id="loginForm"]//label[@id="errorText"]')
    errors += html.findall('.//form[@id="hiddenform"]//label[@id="errorText"]')
    for element in errors:
        if element.text is not None:
            click.echo('Login error: {}'.format(element.text), err=True)
            exit(-1)

    # Retrieve Base64-encoded SAML assertion from form SAMLResponse input field
    for element in html.findall('.//input[@name="SAMLResponse"]'):
        assertion = element.get('value')

    # If we did not get an error, but also do not have an assertion,
    # then the user needs to authenticate
    if not assertion:
        return None, None, None

    # Parse the returned assertion and extract the authorized roles
    saml = ET.fromstring(base64.b64decode(assertion))

    # Find all roles offered by the assertion
    raw_roles = saml.findall(
        './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/Role"]/{*}AttributeValue'
    )
    aws_roles = [element.text.split(',') for element in raw_roles]

    # Note the format of the attribute value is provider_arn, role_arn *OR* role_arn, provider_arn
    # AWS accepts either, and uses role_arn, provider_arn in examples at https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_create_saml_assertions.html
    # but provider_arn, role_arn in the commonly referenced blog post at https://aws.amazon.com/blogs/security/aws-federated-authentication-with-active-directory-federation-services-ad-fs/
    # Since aws-adfs originally assumed provider_arn, role_arn and the rest of the code expects that we'll normalise everything to that order here
    principal_roles = []
    for role in aws_roles:
        if len(role) == 2:
            if ':saml-provider/' in role[0] and ':role/' in role[1]:
                principal_roles.append( role )
            elif ':saml-provider/' in role[1] and 'role' in role[0]:
                principal_roles.append( role[::-1] )

    aws_session_duration = default_session_duration
    # Retrieve session duration
    for element in saml.findall(
            './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/SessionDuration"]/{*}AttributeValue'
    ):
        aws_session_duration = int(element.text)

    return principal_roles, assertion, aws_session_duration

def extract_file(file):
    if not os.path.exists(file) or not os.path.isfile(file):
        click.echo('SAML assertion file was not found or invalid: {}'.format(file), err=True)
        exit(-1)

    assertion = ''

    with open(file, "r+") as f:
        assertion = f.read()

    # Parse the returned assertion and extract the authorized roles
    saml = ET.fromstring(base64.b64decode(assertion))

    # Find all roles offered by the assertion
    raw_roles = saml.findall(
        './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/Role"]/{*}AttributeValue'
    )
    aws_roles = [element.text.split(',') for element in raw_roles]

    # Note the format of the attribute value is provider_arn, role_arn
    principal_roles = [role for role in aws_roles if ':saml-provider/' in role[0]]

    aws_session_duration = default_session_duration
    # Retrieve session duration
    for element in saml.findall(
            './/{*}Attribute[@Name="https://aws.amazon.com/SAML/Attributes/SessionDuration"]/{*}AttributeValue'
    ):
        aws_session_duration = int(element.text)

    return principal_roles, assertion, aws_session_duration
