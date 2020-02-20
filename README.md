# TS-Extractor
An interactive graph visualization system to enable users to extract, analyze and expand relevant subgraphs.

Online demo: http://jalamao.top

Our input is a large graph that contains thousands or more nodes and has node attributes (i.e., semantic information).

The major goal of this project is to help the user explore a large graph by extracting a subgraph (context) relevant to the user-specified nodes (called focus nodes). The extracted subgraph should contain as many nodes sharing the same/similar attribute values with the focus nodes as possible, which can provide the user with clear semantics.
## Setup
It is recommended to install this system in the ubuntu system.
### Server
1. To install the dependency packages of the system server, under the project dir "Server", run:

`pip install -r requirements.txt`

2. Under the project dir "Server/DB", Unzip the database files.

3. Run the file "Vue_Flask_App.py".
### FrontEnd
1. Install Node.js.

2. To install the dependency packages of the system frontend, under the project dir "FrontEnd", run:

`npm install`

3. Under the project dir "FrontEnd", run:

`Sudo npm run dev`

4. Access at http://localhost:8080.
