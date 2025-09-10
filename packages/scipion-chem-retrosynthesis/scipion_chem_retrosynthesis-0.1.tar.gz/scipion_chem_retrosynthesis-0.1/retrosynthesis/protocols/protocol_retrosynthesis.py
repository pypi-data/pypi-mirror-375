################ VERÓNICA GAMO PAREJO ##############################

# General imports 
import gzip, json, os, shutil
from urllib.request import urlopen

# Specific imports
from pyworkflow.protocol.params import PointerParam, STEPS_PARALLEL, StringParam
from pyworkflow.utils.path import moveFile, cleanPath
from pwem.protocols import EMProtocol

from pwchem.utils import *
from pwchem.constants import RDKIT_DIC
from pwchem.objects import SmallMolecule, SetOfSmallMolecules

from retrosynthesis.constants import AIZYNTHFINDER_DIC
from retrosynthesis import Plugin

class ProtChemAiZynthFinder(EMProtocol):

    """ Retrosynthesis of molecules with AiZynthFinder"""
    
    _label = 'aiZynthFinder'
    
    def __init__(self, **kwargs):
        EMProtocol.__init__(self, **kwargs)
        self.stepsExecutionMode = STEPS_PARALLEL
        
    def _defineParams(self, form):
    
        form.addSection(label='Input')
                      
        form.addParam('inputSet', PointerParam, pointerClass="SetOfSmallMolecules",
                      label='Set of molecules to use:', allowsNull=False,
                      help='Select the set of small molecules for retrosynthesis.')
        
        form.addParam('inputLigand', StringParam, label='Selected just one ligand file:',
                      help='Relative path to the ligand file for the retrosynthesis.')
        
                   
    def _insertAllSteps(self):
        self._insertFunctionStep('identifyStep')
        self._insertFunctionStep('createOutputStep')

    def identifyStep(self):
        myLigand=str(self.inputLigand)
        for mol in self.inputSet.get():
            if str(mol.getMolName()) in myLigand:
                ligand_file=mol.getFileName()
        if not ligand_file:
            raise ValueError("No ligand file provided.")
        
        ligand_smiles = self.getSMI(ligand_file,1)
        print("SMILES for retrosynthesis:", ligand_smiles)
        self.runAiZynthFinder(ligand_smiles)

            
    def getSMI(self, mol, nt):
        ''' Generates a SMILES representation of a molecule from a given input file'''
        fnSmall = os.path.abspath(mol)
        fnRoot, ext = os.path.splitext(os.path.basename(fnSmall))

        if ext != '.smi':
            outDir = os.path.abspath(self._getExtraPath())
            fnOut = os.path.abspath(self._getExtraPath(fnRoot + '.smi'))
            args = ' -i "{}" -of smi -o {} --outputDir {} -nt {}'.format(fnSmall, fnOut, outDir, nt)
            Plugin.runScript(self, 'rdkit_IO.py', args, env=RDKIT_DIC, cwd=outDir)    
        return self.parseSMI(fnOut)
        
    def parseSMI(self, smiFile):
        smi = None
        with open(smiFile) as f:
            for line in f:
                smi = line.split()[0].strip()
                if not smi.lower() == 'smiles':
                    break
        return smi
    
    def runAiZynthFinder(self, smi):

        # SAVE SMILE TO TXT FILE
        smiles_file = self._getExtraPath("smiles.txt")
        with open(smiles_file, 'w') as f:
            f.write(smi)
            print(f"SMILES {smi} saved to {smiles_file}")

        # RUN AIZYNTHFINDER
        relative_dir=Plugin.getHome()
        absolute_dir= os.path.join(relative_dir, "config.yml")
        args = f"--config {absolute_dir} --smiles {smiles_file}"
        Plugin.runAIZYNTH("aizynthcli", args)

        #JSON FILE 
        fnJson = self._getExtraPath("output.json.gz")
        moveFile("output.json.gz", fnJson)
        with gzip.open(fnJson, 'rb') as f_in:
            with open(self._getExtraPath("output.json"), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        outDir = os.path.abspath(self._getExtraPath())
        jsonPath= os.path.abspath(self._getExtraPath("output.json"))
        args = '{} {}'.format(jsonPath, outDir)
        scriptPath=Plugin.getScriptsPath()
        Plugin.runScript(self, "retrosynthesis_script.py" ,args, env=AIZYNTHFINDER_DIC,cwd=None, scriptDir=scriptPath)
        cleanPath(fnJson)


    def createOutputStep(self):
        
        outputSmallMolecules = SetOfSmallMolecules().create(outputPath=self._getPath(), suffix='SmallMols')
        molecule_counter = 1
        file_path = self._getExtraPath("output.json")

        try:
            with open(file_path, 'r') as f:
                data_json = json.load(f)
            stock_info = data_json['data'][0]['stock_info']
            smiles_list = list(stock_info.keys())
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return
        except Exception as e:
            print(f"Error opening JSON file: {e}")
            return


        smiles_to_molecule_info = {}
        print("-----------------INITIAL REACTANTS------------------")
        for smile in smiles_list:
                file_name=f"Molecule_{molecule_counter}"
                sdf_filename = os.path.abspath(os.path.join(self._getExtraPath(), f"{file_name}.sdf"))
                
                outDir = os.path.abspath(self._getExtraPath())
                args = '--smiles "{}" --output-directory "{}" --filename "{}"'.format(smile,outDir, file_name)
                scriptPath=Plugin.getScriptsPath()
                Plugin.runScript(self, "convert_smiles_to_sdf_script.py" ,args, env=AIZYNTHFINDER_DIC,cwd=None, scriptDir=scriptPath)
                
                cid, link  = self.getCIDFromSmiles(smile)
                name = self.getMainNameFromCID(cid)
                if name is not None:
                    name = name.lower()
                else:
                    name=smile
                smallMolecule = SmallMolecule(smallMolFilename=sdf_filename)
                smallMolecule.setMolName(name)
                outputSmallMolecules.append(smallMolecule)
                smiles_to_molecule_info[smile] = {
                    'name': name,
                    'counter': molecule_counter,
                    'url': link
                }
                molecule_counter += 1 
                print(f"{file_name} --> SMILES: {smile}  ||  NAME: {name} || URL: {link}")

        outputSmallMolecules.updateMolClass()
        self._defineOutputs(outputSmallMolecules=outputSmallMolecules)

        trees_info=data_json['data'][0]['trees']
        parent_child_relationships = {}
        def extract_smiles_and_relationships(data, parent_smiles=None):
            for tree in data:
                smiles = tree.get('smiles')
                if smiles and '>>' not in smiles:
                    if parent_smiles:
                        if parent_smiles not in parent_child_relationships:
                            parent_child_relationships[parent_smiles] = {'parent': None, 'children': []}
                        parent_child_relationships[parent_smiles]['children'].append(smiles)
                        
                        parent_child_relationships[smiles] = {'parent': parent_smiles, 'children': []}
                    else:
                        parent_child_relationships[smiles] = {'parent': None, 'children': []}

                if 'children' in tree:
                    if '>>' in smiles:
                        extract_smiles_and_relationships(tree['children'], parent_smiles)
                    else:
                        extract_smiles_and_relationships(tree['children'], smiles)

        extract_smiles_and_relationships(trees_info)

        for smiles, relations in parent_child_relationships.items():
            if smiles in smiles_to_molecule_info:
                parent_info = smiles_to_molecule_info[smiles]
                parent_counter = parent_info['counter']
                parent_name = parent_info['name']
                parent_url= parent_info['url']
                parent_url = parent_url.replace("cids/TXT", "")
            else:
                molecule_counter += 1
                try:
                    cid_parent, parent_url = self.getCIDFromSmiles(smiles)
                    parent_url = parent_url.replace("cids/TXT", "")
                    parent_name = self.getMainNameFromCID(cid_parent)
                except Exception as e:
                    parent_name = "Unknown"  # Handle the case where CID retrieval fails

                smiles_to_molecule_info[smiles] = {
                    'name': parent_name,
                    'counter': molecule_counter,
                    'url': parent_url
                }
                parent_counter = molecule_counter

            children_info = []
            for child in relations['children']:
                if child in smiles_to_molecule_info:
                    child_info = smiles_to_molecule_info[child]
                    child_counter = child_info['counter']
                    child_name = child_info['name']
                    child_url= child_info['url']
                    child_url = child_url.replace("cids/TXT", "")
                else:
                    molecule_counter += 1
                    try:
                        cid_child, child_url= self.getCIDFromSmiles(child)
                        child_url = child_url.replace("cids/TXT", "")
                        child_name = self.getMainNameFromCID(cid_child)
                    except Exception as e:
                        child_name = "Unknown"  # Handle the case where CID retrieval fails

                    smiles_to_molecule_info[child] = {
                        'name': child_name,
                        'counter': molecule_counter,
                        'url': child_url
                    }
                    child_counter = molecule_counter

                children_info.append((child_counter, child_name,child_url, child))

            print("---------------------------------------------------------------------")
            print(f"  Product: Molecule {parent_counter} - SMILES: {smiles} - NAME: {parent_name} - URL: {parent_url}")
            if not children_info:
                print("  It is an initial reactant")
            else:
                for i, (child_counter, child_name, child_url, child_smiles) in enumerate(children_info):
                    print(f"  Reactant {i+1}: Molecule {child_counter} - - SMILES: {child_smiles} - NAME: {child_name} - URL: {child_url}")


    
    def getCIDFromSmiles(self, smi):
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/%s/cids/TXT" % smi
        try:
            with urlopen(url) as response:
                cid = response.read().decode('utf-8').split()[0]
        except Exception as e:
            cid = None
        return cid, url
     
    def getMainNameFromCID(self,cid):
        url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{}/synonyms/TXT".format(cid)
        try:
            with urlopen(url) as response:
                r = response.read().decode('utf-8')
                synonyms = r.strip().split('\n')
                
                if synonyms:
                    main_name = synonyms[0].strip()
                else:
                    main_name = None
                
        except Exception as e:
            main_name = None
        
        return main_name
    
    