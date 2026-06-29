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

The simple version of biobert, with embeddings based on AAL3v1 regions of the brain but with no extra pre-training works well only when the text is closely related to the name of the region. The probability of each region is listed in the brackets. 
![alt text](image.png)

The more complex version of biobert, trained on annotated PubMed abstracts. The dictionary comes from the AAL3v1 atlas with 170 unique brain regions.
![alt text](image.png)

The most complex model was trained on hierarchical embeddings. AAL atlas has brain regions that are extremely common (hippocampus) and others that are quite rare. The goal is to highlight the most relevant regions.
![alt text](image.png)

#References
1. Medium NER tutorial [link](https://medium.com/@maneyogesh065/fine-tuning-biobert-for-custom-named-entity-recognition-a-complete-guide-a05b124edda0)
2. BioBERT-CRF paper [link](https://onlinelibrary.wiley.com/doi/full/10.15302/J-QB-022-0302)
3. How to choose tools for unique BioNER need [link](https://www.sciencedirect.com/org/science/article/pii/S1874120724000031)
4. BioSERPBERT repository of neuroscience representation of brain region text mining [link](https://github.com/Brainsmatics/BioSEPBERT)
5. Connectivity search engine with different connected embeddings [link](http://atlas.brainsmatics.org/res/BioSEPBERT/)