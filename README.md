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
The code should update an XML file stored in a GCP Bucket folder previously created. The Public URL of that file is accessible to the internet which means that we can replace the original RSS (XML file) feed URL with this Public URL.
5. Create Scheduler Job
->Add Name, Frequency (in cron job format) and Timezone
->Select ‘Pub/Sub’ as Target type
->Select the Topic created above as Cloud Pub/Sub topic
->Write a Message body
Rest of the options: default
## Testing
After setting up the scheduled function, you can test it by clicking on it > TESTING > TEST THE FUNCTION.

