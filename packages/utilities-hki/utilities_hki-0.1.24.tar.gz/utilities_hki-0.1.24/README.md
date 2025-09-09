# Global Utilities

> last modified 8 March 2023 by Colleen Treado

The `utilities-hki` repository contains the common utilities required by multiple other `humankind-datascience` repositories. Unlike the old `utilities` repo, this package contains no encrypted files, and credentials are now passed into the utility functions as input arguments.

## Current status
This repository is the code repository for the `utilities-hki` pip package, which, together with the new `credentials` repository, replaces the current `utilities` submodule in the other repositories used for data science at Humankind. The package was created by following [this guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) and the package can be found on [PyPI](https://pypi.org/project/utilities-hki/). Most of our repositories have been updated to import the new `utilities-hki` pip package and call the updated utility functions, passing in the credentials from the new `credentials` repo, instead. The repositories that still need to be updated are
- daily_volume_predict
- volume_predict (but this is not in use)
- facebook_ads


## Installation and setup

For first-time setup, clone the repository into a fresh work area:

```bash
# cloning via ssh is preferred but requires an ssh key connection in your account
git clone git@github.com:humankind-datascience/utilities-hki.git
```

The code requires a number of Python packages to run, which should be installed inside of a dedicated virtual environment. The preferred virtual environment tool is [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/).

To install the required packages in a new virtual environment, run the following command from the top-level directory of the git repository:
```bash
pip install -r requirements.txt
```

If additional packages need to be installed upon changes to the code, add them to the `requirements-top-level.txt` file. Then run the below commands to install (and upgrade) the top-level dependencies and update the `requirements.txt` file for future use.
```bash
pip install -r requirements-top-level.txt --upgrade
pip freeze -r requirements-top-level.txt > requirements.txt
```

Additionally, the AWS Command Line Interface (AWS CLI) is required for use of the botocore library, which is used in database utilitify functions to read from and write to the AWS RDS databases. See the [AWS CLI documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html) for installation instructions.

Now you can run the top-level scripts:

```bash
python <utilities-script.py>
```

The `utilities-hki` repository contains only testing top-level scripts, designed to test the utility functions during package development.


## Code updates

When making changes to the code, follow [GitHub flow](https://docs.github.com/en/get-started/quickstart/github-flow), i.e. create a new branch, make changes on that branch, frequently committing and pushing those changes to that branch, and then create a pull request to merge those changes into master upon review and approval.


## Utility code overview

The `utilities-hki` repository contains common utility functions used across repositories in the Humankind Data Science code base. The utility functions are grouped by type into separate modules, as outlined below.

- **analy_utils**: analysis utility functions, including cleaning procedures for and assignment of engagement types to the visit-level data;
- **db_utils**: database utility functions;
- **email_utils**: email utility functions;
- **fb_utils**: Facebook Ads utility functions.

Standard cleaning of the visit-level data should be implemented at the start of any analysis and can be achieved by calling the `analy_utils.clean_visits` function (see the docstrings for more details.

Sample code for applying the trained clustering model and assigning the letter/numeric grades to the engagement types for each visit is provided below, where `visit` is a DataFrame. Read the docstrings for assign_cluster() and get_cluster_grades() for more details.

```
from utilities-hki import analy_utils
# assumes visit data has already been pulled or loaded into visit

engagement = analy_utils.assign_cluster(visit)
engagement = engagement.reset_index().merge(
    analy_utils.get_cluster_grades(), how='left', on='engagement_type')
visit = visit.merge(engagement, how='inner', on='visit_id')
```
