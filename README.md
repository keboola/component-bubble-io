# Bubble.io extractor

Download data from endpoints exposed by your Bubble.io application.

**Table of contents:**  
  
[TOC]

# Configuration
 
## Api URL

Your general Data api endpoint url. It follows this pattern:
 
`https://[appname].bubbleapps.io/api/1.1/obj/` or `https://[yourdomain].com/api/1.1/obj/`

Replace the placeholders  `[]` with your app specific values.

## API token

Bubble API token.

## Modified date interval setup

### Period from date

[Exclusive] Date in YYYY-MM-DD format or dateparser string i.e. 5 days ago, 1 month ago, yesterday, etc. 
If left empty, no boundary is set.

### Period to date

[Exclusive] Date in YYYY-MM-DD format or dateparser string i.e. 5 days ago, 1 month ago, yesterday, etc. 
If left empty, no boundary is set.

### **Important functionality note**

In some cases the API might timeout on queries that return more than 50k results. For that reason the extraction will 
fail asking you to limit the query by specifying lower interval.

## Objects

List of the data objects exposed by the data API as defined in the Bubble

### Object name

Name of the object / data api endpoint as defined in the Bubble.io UI.

### Load type

If set to Incremental update, the result tables will be updated based on primary key. 
Full load overwrites the destination table each time.

### Object fields

Comma separated list of fields to extract from the object, each value has to be enclosed in " double quote characters. 

**Note:** The system fields ["_id", "_type", "Creator", "Created Date", "Modified Date"] are always included by default, 
if you include them nevertheless it won't have any effect.

**Example value**: `"UserName","Value", "Cost"`

# Results

Each endpoint will output a single table named as the endpoint name. Apart from selected columns each table will include 
following system columns by default, regardless the `fields` parameter setup:

`Creator`, `Created Date`, `Modified Date`, `_id`, `_type`

**NOTE** KBC Storage cannot store `_` prefixed columns so these will be prefixed with `bubbleinternal` prefix. 

Therefore each table will contain: `Creator`, `Created Date`, `Modified Date`, `bubbleinternal_id`, `bubbleinternal_type` 
columns.

 
# Development
 
This example contains runnable container with simple unittest. For local testing it is useful to include `data` folder in the root
and use docker-compose commands to run the container or execute tests. 

If required, change local data folder (the `CUSTOM_FOLDER` placeholder) path to your custom path:
```yaml
    volumes:
      - ./:/code
      - ./CUSTOM_FOLDER:/data
```

Clone this repository, init the workspace and run the component with following command:

```
git clone https://bitbucket.org:kds_consulting_team/kds-team.ex-ms-sharepoint.git my-new-component
cd my-new-component
docker-compose build
docker-compose run --rm dev
```

Run the test suite and lint check using this command:

```
docker-compose run --rm test
```

# Integration

For information about deployment and integration with KBC, please refer to the [deployment section of developers documentation](https://developers.keboola.com/extend/component/deployment/) 