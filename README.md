# modRSSgcp
This repository contains code that allows to extract RSS feeds from multiple sources, modify them and pack them to be served as periodically-triggered Google Cloud Functions, using Pub/Sub Topics and Google Cloud Scheduler. More info: https://cloud.google.com/scheduler/docs/tut-pub-sub

## Instructions
Instead of feeding the original RSS feed to your ingestor, we can pass it through a Google Cloud Function that will periodically generate a modified RSS feed file with the changes that we want, for example, the author of the article added to the title.
For creating this service that periodically updates the modified feed file we need three Google Cloud Platform features: Pub/Sub Topics, Functions, and Scheduler.
1. Create Google Cloud account
2. Create Project
3. Create Topic:
->Add name (e.g. “test-topic”)
Rest of the options: default
4. Create Function
   ->Add name (e.g. “test-function”)
->Select 'Cloud Pub/Sub' as Trigger type
   ->Select the Topic you just created
   Rest of the options: default
   Click Save > In the source code window, create a main.py file and paste the code that will be executed by the Function (in this repository, that is the code in `main.py`). Also create a `requirements.txt` file with the libraries needed for the execution of the Function code.
   The code should update an XML file stored in a GCP Bucket folder previously created. The Public URL of that file is
   accessible to the internet which means that we can replace the original RSS (XML file) feed URL with this Public URL.
5. Create Scheduler Job
   ->Add Name, Frequency (in cron job format) and Timezone
   ->Select ‘Pub/Sub’ as Target type
   ->Select the Topic created above as Cloud Pub/Sub topic
   ->Write a Message body
   Rest of the options: default

## Testing

After setting up the scheduled function, you can test it by clicking on it > TESTING > TEST THE FUNCTION.

## Developer Tips

### Using IntelliJ

In order to open the project directly from GitHub, you need to login
to your account on IntelliJ (which you can do in Settings) and also
allow access to the Nonlinear-EA organization through your account using
[this link](https://github.com/settings/connections/applications/58566862bd2a5ff748fb).

To set up the Python interpreter, follow these steps:

1) Go to File>Project Structure.
2) Go to SDKs, click the + button on the left (not the one on the right), select Setup Python SDK.
3) Make sure virtualenv is selected. Select the latest version of Python you have on your system (I'm using 3.11). Click
   OK.
4) Click Project, and then select the SDK you just created from the dropdown. Click OK.

Also, it's going to be more convenient if you're using IntelliJ if you automatically format the code before you commit
it. You can do so following these steps:

1) Go to Settings.
2) Select Editor>Code Style then for Scheme select IDE Default. (This scheme follows the PEP standards. If we all use
   the same scheme, it'll prevent us from reformatting each other's code. Any contributors not using IntelliJ can
   probably avoid most reformattings by just using a formatter that follows PEP.)
3) Select Git>Commit to open the Commit dialog.
4) Check the "Reformat Code", "Rearrange Code", "Optimize Imports" boxes. If you're using the modal dialog, you need to
   select the little gear icon to see these checkboxes.

IntelliJ will show you little warnings when your code goes past the line limit, or you have too many lines between
your method signatures. I suggest disabling these warnings when they come up, and checking the boxes mentioned above so
the IDE automatically formats the code for you. This'll save you time.
