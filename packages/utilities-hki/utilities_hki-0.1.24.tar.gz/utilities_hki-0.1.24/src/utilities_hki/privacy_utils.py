"""
Adherence to Data Privacy and Security Procedures
"""

P3_descriptors = [
    # field names from Apex SOD files
    'TaxIDNumber',
    'AccountNumber',
    # field names from roboadvisor backend
    'apex_account_id',
    'user_id' # cognito user id
]


# FUNCTIONS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def check_recipients(recipients, read_authorization, classification= 'P2'):
    """
    Check that the recipients have P2 authorization.

    Parameters
    ----------
    recipients : str or list of str
        List of email addresses.
    read_authorization : dict
        Dictionary of email addresses and their privacy classification.
    classification : str, optional
        Privacy classification to check against. The default is 'P2'.

    Returns
    -------
    bool
        True if all recipients have the authorization, False otherwise.
    """
    if isinstance(recipients, str):
        recipients= [s.strip() for s in recipients.split(',')]

    for recipient in recipients:
        if recipient not in read_authorization.keys():
            return False
        else:
            if classification not in read_authorization[recipient]:
                return False
    return True

def below_size_limit(data):
    """
    Check that the data is below the size limit for P2 data. P2 data with more than 500 rows is not allowed.

    Parameters
    ----------
    data : pd.DataFrame or iterable
        Data to check.

    Returns
    -------
    bool
        True if the data is below the size limit, False otherwise.
    """
    # raise an error if the data is a string
    if isinstance(data, str):  raise TypeError('Data cannot be a string')
    
    P2_max_size = 500
    if len(data) > P2_max_size:
        return False
    else:
        return True
    
def contains_P3(content, exceptions=[]):
    """
    Check if the content contains P3 data.

    Parameters
    ----------
    content : str
        Email content.
    exceptions : list of str, optional
        List of P3 descriptors to ignore if they have been anonymized or replaced
        with non-P3 data. The default is [].

    Returns
    -------
    bool
        True if the content contains P3 data, False otherwise.
    """
    for descriptor in P3_descriptors:
        if (descriptor in content) and (descriptor not in exceptions):
            return True
    return False
