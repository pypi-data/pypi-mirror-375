============================
MPLAB® Machine Learning SDK
============================

The MPLAB ML SDK provides a programmatic interface to MPLAB ML Development Suite REST API's for building machine learning pipelines including data processing, feature generation, and classification for developing smart sensor algorithms optimized to run on Microchip Technology MCUs and MPUs.

Installation/Setup Instructions
===============================

1. The MPLAB ML SDK requires **python version 3.7 or greater** to be installed on your computer.
2. We recommend running the MPLAB ML SDK using Jupyter Notebook. Install Jupyter Notebook by opening a command prompt window on your computer and running the following command

    pip install jupyter

3. Next, to install the MPLAB ML SDK open a command prompt window on your computer and run the following command

    pip install MPLABML

This command will install the MPLAB ML SDK and all of the required dependencies on your computer.

Connect to the MPLAB ML Development Suite Server
------------------------------------------------

Once you have installed the ML SDK, you can connect to the server by running the following

    from mplabml import*

    client = Client()

You will then be prompted to input your API key, which can be obtained by logging into the MPLAB ML Model Builder and clicking from the user profile menu at the top right of the screen.

Creating an Account
-------------------

Connecting to the MPLAB ML Development Suite server requires an account. You can purchase a license on Microchip Direct (https://www.microchipdirect.com/)

Documentation
-------------

Documentation for the ML SDK can be found on the Microchip Online Docs (https://onlinedocs.microchip.com/v2/keyword-lookup?keyword=MPLAB-ML-SDK-Documentation&redirect=true)
