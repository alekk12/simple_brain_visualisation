# Brain Visualisation
Local AI tool, based on finetuned BioBERT, for visualising different brain regions from text description.

Setup
1. Start with this command.
`npm install`
This will install the necessary libraries, depending on the existing version of node installed some errors need to be resoled.
2. After this, create local.config.json based on template_local.config.json. This defines which model will be used to predict the brain regions. Update config.json if localhost:3000 is busy with another process.
3. Create conda env for running the model. 
   `conda env create -f environment.yml`
4. Start the server with visualisations.
`npm start`
This will start the npm server at localhost:3000. 

The available functionalities are listed below.
* Uploading pdf/html file.
* Opening the file in a browser.
* Highlighting the text connects to the model, that read the text, and generates the image. The image is also saved in the `output` directory.

# Results

The simple versio of biobert, with embeddings based on AAL3v1 regions of the brain but with no extra pre-training works well only when the text is closely related to the name of the region.
![alt text](image.png)