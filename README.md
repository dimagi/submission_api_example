Submission API Example
======================

**submit_data.py** is an example script to illustrate how to use the
CommCare HQ Submission API.


Code as documentation
---------------------

To see how to use the CommCare HQ Submission API for your own use case,
or in your own language, it is best to get an overview of the workflow,
and then dive into the details.

Start at the `main()` function in **submit_data.py**. You will see that
data is cast as a list of cases, then rendered as an XForm, and finally
submitted to CommCare HQ.

Notice the `Case` class to see what a case looks like.

The `get_data()` function is arbitrary. The script uses CSV because it
is simple, but your use case is probably going to be different. The
point is just to return data that can be cast as cases.

Take a look at **xform_template.xml** to see the structure of an XForm,
and how case data is stored in it.

**NOTE**: This is a simplistic example that always creates new cases; it
does not update existing ones. If this is not the behaviour you want,
you will need to keep a record of cases that have already been created.

(If you would like to adapt this example not to try to create cases that
have already been created, you can set the `server_modified_on`
attribute for existing cases.)



Requirements
------------

* Python 3.8+


Installation
------------

    $ pip install -r requirements.txt


Usage
-----

1. Edit the script to configure the settings with your values at the
   top.

2. Set environment variables with your CommCare username, password and
   user ID. You can find your user ID in the URL of your user details
   page. e.g. "....commcarehq.org/a/my-project-space/settings/users/web/account/
   **c0ffeeeeeb574eb8b5d5036c9a61a483** /"

3. Run the script:

       $ export CCHQ_USERNAME=user@example.com
       $ export CCHQ_PASSWORD=M7MwnA7okswFXwKC
       $ export CCHQ_USER_ID=c0ffeeeeeb574eb8b5d5036c9a61a483
       $ submit_data.py sample_data.csv
