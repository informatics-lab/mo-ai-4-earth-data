

## Setup

* Install the [Azure functions core tools](https://github.com/Azure/azure-functions-core-tools).
* Install the [AZ CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest)
* `python -m venv ./env`
* `source env/bin/activate`
* `pip3 install -r __app__/requirements.txt`
* Run `cd __app__; func init` in project root.
* Run `cd __app__; func settings add APIKEY <SERVICE HUB KEY>`


## Run locally

You can run locally but this will connect to the live azure resources. You are better using the unit tests or creating new ones. You can change your local settings `func settings add MY_SETTING MY_VALUE` to avoid this but it would be easy to accidentally publish them to the live function.

### Run:

If running for first time on a machine you may wish to pull down remote settings `cd __app__; func azure functionapp fetch-app-settings; cd ..`

If installing from scratch you'll need to set up resources using `./scripts/set_up_resources.sh`.

You can use `ngrok http 7071` to test integration with external services if required.

To run: `func start`

### Test:
`pytest`

Or with logging info: `pytest  --log-cli-level info`


## Subscribing

To hide keys and urls the subscription notebook is stored in the `private-config` repo.

Soft link in the notebook.
`ln -s <path to private repo>/service-hub/subscribe-to-service-hub.ipynb` `notebooks/subscribe-to-service-hub.ipynb`

Run the notebook server

`jupyter lab --notebook-dir notebooks`

Open the notebook `subscribe-to-service-hub.ipynb` and subscribe and or delete subscriptions. 

When testing using `ngrok` or similar change the value of `SUB_URL` to your https `ngrok` url. 
If deployed change `SUB_URL` to your deployed app url

When testing (or deployed) you may need to either restart ngrok to get a new url or delete and recreate your subscription to force service hub to retry on subscription it's already received. You can do this in the notebook.

**Careful when deleting subscriptions. Other services use these subscriptions (i.e. AWS Earth)**

Once subscribed using the notebook above you'll need to confirm the subscription. This can be done by either viewing the log output when the subscription is created or use notebook `get-messages-from-sub-queue.ipynb`. The subscription confirmation queue has messages with a url that needs to be visited to confirm the subscription.


## Publish / deploy

`./scripts/set_up_resources.sh`
`./scripts/update.sh`

If no infrastructure changes `./scripts/update.sh` alone should be sufficient.

If deploying for first time from a machine you may wish to pull down remote settings `cd __app__; func azure functionapp fetch-app-settings; cd ..`. 