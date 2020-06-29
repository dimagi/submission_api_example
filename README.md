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

Take a look at **xform.xml.j2** to see the structure of an XForm, and
how case data is stored in it.

**NOTE:** This is a simplistic example that always creates new cases; it
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

1. Clone this repository

       $ git clone https://github.com/dimagi/submission_api_example.git
       $ cd submission_api_example

2. Create and activate a virtual environment

       $ python3 -m venv venv
       $ source venv/bin/activate

3. Install required Python packages

       $ pip install -r requirements.txt


Usage
-----

1. Set environment variables with your configuration:

       $ export CCHQ_PROJECT_SPACE=my-project-space
       $ export CCHQ_CASE_TYPE=person
       $ export CCHQ_USERNAME=user@example.com
       $ export CCHQ_PASSWORD=MijByG_se3EcKr.t
       $ export CCHQ_USER_ID=c0ffeeeeeb574eb8b5d5036c9a61a483
       $ export CCHQ_OWNER_ID=c0ffeeeee1e34b12bb5da0dc838e8406

   * `CCHQ_CASE_TYPE` is a name for the type of cases you will be
     importing. This is usually something like "person", or "site".

   * You will need your CommCare credentials: username, password and
     user ID. If you navigate to your user details page, you can find
     your user ID in the URL. e.g.
     "....commcarehq.org/a/my-project-space/settings/users/web/account/
     **c0ffeeeeeb574eb8b5d5036c9a61a483** /"

   * CommCare determines who has access to the cases that you import
     based on the location or mobile worker that is set as the owner. As
     you found your user ID, navigate to the details page for the mobile
     worker or location to get their ID from the URL.

2. (Optional) Edit the script to set an XML namespace to identify your
   XForm submission, and a string to identify the origin of your data.

3. Run the script:

       $ ./submit_data.py sample_data.csv
