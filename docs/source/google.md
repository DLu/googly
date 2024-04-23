# Setting Up with Google

To develop using the Google APIs you need to set up a few things with your Google account.
You may choose to follow
[The Official Documentation for Getting Started](https://developers.google.com/workspace/guides/get-started),
but we'll hit the key points here. You'll have to do all this regardless of whether you use the [provided Python bindings](https://developers.google.com/sheets/api/quickstart/python) or the googly library.

## Step 1: Google Cloud Project

The first thing you need is an overarcing project that you can use for all your code.

  1. Visit [The Google Cloud Console](https://console.cloud.google.com/).
  1. Agree to terms of service with the Google Account you wish to use (if needed)
  1. At the top of the page, there should be a widget to "Select a project"
     ![Select a project widget](_static/SelectAProject.png)

     If there are no projects available, you'll need to create one.
     a. To create a project, click New Project, and then enter a project name.
  1. Once you have selected your project, it should look like this:
     ![Selected project widget](_static/SelectedProject.png)

## Step 2: Credentials

Next, you'll need to create a method for authenticating with your project.

  1. Visit [the Credentials page](https://console.cloud.google.com/apis/credentials).
  1. Click "Create Credentials" at the top of the screen.
  1. Select "OAuth client ID"
  1. Pick an Application Type. Desktop App seems appropriate for many little Python scripts.
  1. Download the credentials JSON and save it as `secrets.json` alongside the code you will be running.

## Step 3: Enable APIs

You will need to enable each separate API you want to use. You can search for them [in the APIs library](https://console.cloud.google.com/apis/library) or jump to them directly below.
  * [Calendar](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
  * [Drive](https://console.cloud.google.com/apis/library/drive.googleapis.com)
  * [GMail](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
  * [Photos](https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com)
  * [Sheets](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
  * [YouTube](https://console.cloud.google.com/apis/library/youtube.googleapis.com)

## Step 4: Test Users

If you are using some sensitive bits of the APIs, then you will either need to "publish" your application, or you can manually add users that can use your code. The latter is infinitely easier if you're just working with your own data. Both can be done from the [consent screen configuration](https://console.cloud.google.com/apis/credentials/consent)
