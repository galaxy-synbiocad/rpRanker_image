import cobra
import itertools
import os
from cameo.strain_design import OptKnock
import libsbml
from hashlib import md5
import logging

#TODO: define the biomass parameter here to be used. The default should be the BIGG (R48E37591)
class FBA:
    def __init__(self, outputPath=None, biomassID='R48E37591'):
        if outputPath and outputPath[-1:]=='/':
            outputPath = outputPath[:-1]
        self.outputPath = outputPath
        self.biomassID = biomassID
        self.rp_sbml_paths = None
        self.rp_sbml_models = None
        self.results = None

    ############################### PRIVATE FUNCTIONS ############################


    #TODO: export the models into SBML, controlling the versions
    #TODO: export the heterologous reactions into SBML format
    def _exportSBML(self, type_name, model, model_id, inputType, path=None):
        """
        Function to export models generated in libSBML or cobraPy to SBML
        cobra.io.write_legacy_sbml(models[model_id], 
                                    p+'/'+str(model_id)+'.sbml', 
                                    use_fbc_package=False)
        """
        ####### check the path #########
        p = None
        if path:
            if path[-1:]=='/':
                path = path[:-1]
            if not os.path.isdir(path):
                if self.outputPath:
                    p = self.outputPath
                else:
                    logging.error('The output path is not a directory: '+str(path))
                    return False
            else:
                p = path
        else:
            p = self.outputPath
        p += '/'+type_name
        ########## check and create folder #####
        if not os.path.exists(p):
            os.makedirs(p)
        ########## export ###################
        """
        for model_id in models:
            if inputType=='cobrapy':
                cobra.io.write_sbml_model(models[model_id],
                                            p+'/'+str(model_id)+'.sbml', 
                                            use_fbc_package=False)
            elif inputType=='libsbml':
                libsbml.writeSBMLToFile(models[model_id],
                                p+'/'+str(model_id)+'.sbml')
            else:
                logging.error('Cannot recognise input type')
                return False
        """
        if inputType=='cobrapy':
            cobra.io.write_sbml_model(model,
                                        p+'/'+str(model_id)+'.sbml', 
                                        use_fbc_package=False)
        elif inputType=='libsbml':
            libsbml.writeSBMLToFile(model,
                            p+'/'+str(model_id)+'.sbml')
        else:
            logging.error('Cannot recognise input type')
            return False
        return True


    def _nameToSbmlId(self, name):
        """
        Function to rewrite the string for libSBML id to valid format
        """
        IdStream = []
        count = 0
        end = len(name) 
        if '0' <= name[count] and name[count] <= '9':
            IdStream.append('_')
        for count in range(0, end):     
            if (('0' <= name[count] and name[count] <= '9') or
                    ('a' <= name[count] and name[count] <= 'z') or
                    ('A' <= name[count] and name[count] <= 'Z')):
                IdStream.append(name[count])
            else:
                IdStream.append('_')
        Id = ''.join(IdStream)
        if Id[len(Id) - 1] != '_':
            return Id
        return Id[:-1]


    def _checklibSBML(self, value, message):
        """
        Taken from: http://sbml.org/Software/libSBML/docs/python-api/create_simple_model_8py-example.html
        """
        if value is None:
            raise SystemExit('LibSBML returned a null value trying to ' + message + '.')
        elif type(value) is int:
            if value==libsbml.LIBSBML_OPERATION_SUCCESS:
                return
            else:
                err_msg = 'Error encountered trying to ' + message + '.' \
                        + 'LibSBML returned error code ' + str(value) + ': "' \
                        + libsbml.OperationReturnValue_toString(value).strip() + '"'
                raise SystemExit(err_msg)
        else:
            return


    ############################### PUBLIC FUNCTIONS ############################# 


    #function that takes the location of the database, the model of interest, and the RetroPath2.0 output
    #and constructs models including the heterologous pathway
    #def runAll(self, cofactors_rp_paths, rr_reactions, model_compartments, cobra_model, rp_smiles, isCPLEX=False, isExport=False):
    def runAll(self, cofactors_rp_paths, model_compartments, cobra_model, isCPLEX=False, isExport=False):
        """run all the FBA models
            Adds the cofactors to the heterologous pathways and then to the models 
            and runs the models using different objectives
        """
        ############# Changing it so that the functions takes a single path and
        # fills the results in the cofactors_rp_paths
        for path_id in cofactors_rp_paths:
            logging.info('################## FBA Analysis for path '+str(path_id)+'  #####################')
            tmp_model = self.constructModel_cobraPy(cofactors_rp_paths[path_id], 
                                                    path_id, 
                                                    model_compartments, 
                                                    cobra_model, 
                                                    isExport)
            if isCPLEX:
                tmp_model.solver = 'cplex'
            self.simulateBiomass(cofactors_rp_paths[path_id], tmp_model)
            self.simulateTarget(cofactors_rp_paths[path_id], tmp_model)
            self.simulateBiLevel(cofactors_rp_paths[path_id], tmp_model)
            self.simulateSplitObjective(cofactors_rp_paths[path_id], tmp_model)
        return True 


    #TODO: write the function
    def constructModels_liSBML(self):
        return False


    #TODO: rewrite it to match with other functions
    def constructModel_cobraPy(self, cofactors_rp_path, model_id, ori_model_compartments, ori_model, isExport=False, inPath=None):
        """
            Returns a dictionnary of models with the keys the path from RP2paths out_paths.csv
            and the instructions to plot the heterologous pathway (as well as the metabolic sink and the source)
            to generate a plot in networkx
        """
        cytoplasm_compartment = [i for i in ori_model_compartments if ori_model_compartments[i]['short_name']=='c'][0] # this assuming that there is always only one result
        extracellular_compartment = [i for i in ori_model_compartments if ori_model_compartments[i]['short_name']=='e'][0] # this assuming that there is always only one result
        #list all the metabolites in the model. WARNING: works only for MNXM models
        #all_inputModel_metabo = [i.id.split('__')[0] for i in ori_model.metabolites]
        #NOTE: we assume that the metabolites are all in the cytoplasm (apart from the last transport step)
        #TODO: need to flag that the metabolites (sink) first step in the reaction is contained in the model - to validate the rp_path
        ########### METABOLITES #########################
        #create a new model where we will add this path to it
        model = ori_model.copy()
        #enumerate all the different compounds from the path
        #new_meta = list(set([y for i in path for y in itertools.chain(i['right'], i['left'])]))
        new_meta = set([i for step_id in cofactors_rp_path['path'] for i in cofactors_rp_path['path'][step_id]['steps'].keys()])
        all_meta = {}
        for meta in new_meta:
            #remove the ones that already exist in the model
            if not meta in all_meta:
                try:
                    #NOTE: we assume that all the metabolites that we add here are in the cytoplasm
                    #return the metaolite if already in the model
                    all_meta[meta] = model.metabolites.get_by_id(meta+'__64__'+cytoplasm_compartment)
                except KeyError:
                    #if not in the model create a new one
                    all_meta[meta] = cobra.Metabolite(meta, name=meta, compartment=cytoplasm_compartment)
        ############## REACTIONS ##########################
        for step_id in cofactors_rp_path['path']:
            reaction = cobra.Reaction('rpReaction_'+str(step_id))
            #reaction.name = 
            reaction.lower_bound = 0.0 # assume that all the reactions are irreversible
            reaction.upper_bound = 999999.0 #this is dependent on the fluxes of the others reactions
            reaction.gene_reaction_rule = 'rpGene_'+str(step_id)
            reac_meta = {}
            for mnxm in cofactors_rp_path['path'][step_id]['steps']:
                reac_meta[all_meta[mnxm]] = float(cofactors_rp_path['path'][step_id]['steps'][mnxm]['stoichiometry'])
            reaction.add_metabolites(reac_meta)
            model.add_reactions([reaction])
        ################# Extracellular transport of target
        #NOTE: some molecules cannot be exported and thus this step should not be added
        #identify the target molecule
        target_name = [i for i in new_meta if i[:6]=='TARGET'][0]
        #create the metabolite for the extracellular version of the target metabolite
        extracell_target = cobra.Metabolite(target_name+'_e', name=target_name, compartment=extracellular_compartment)
        #Add the export from the cytoplasm to the extracellular matrix ######
        #exportReaction = cobra.Reaction('exportTarget')
        #exportReaction.name = 'ExportTarget'
        exportReaction = cobra.Reaction('targetSink')
        exportReaction.name = 'targetSink'
        exportReaction.lower_bound = 0.0 #default = 0.0
        exportReaction.upper_bound = 999999.0 #default = 1000 TODO: see if changing this changes something
        #these are the bounds for the yeast bigg model
        #TODO: check .reversibility of the reaction after setting these bounds
        #add that metabolite to the 
        #exportReaction.add_metabolites({extracell_target: 1.0, all_meta[target_name]: -1.0})
        exportReaction.add_metabolites({all_meta[target_name]: -1.0})
        #print(exportReaction.data_frame())  
        model.add_reactions([exportReaction])
        ################### Add the sink reaction
        '''
        sinkReaction = cobra.Reaction('targetSink')
        sinkReaction.name = 'TargetSink'
        sinkReaction.lower_bound = 0.0 # we assume that all the reactions are irreversible
        sinkReaction.upper_bound = 999999.0 # this is dependent on the fluxes of the other reactions
        sinkReaction.add_metabolites(
            {extracell_target: -1.0})
        model.add_reactions([sinkReaction])
        '''
        if isExport:
            self._exportSBML('sbml_models', model, model_id, 'cobrapy', inPath)
        return model




    #TODO: change the function to update the cofacors_rp_paths instead of returning a new parameter
    def OLD_constructPaths_libSBML(self, cofactors_rp_paths, isExport=False, inPath=None, compartment='MNXC3'):
        """
        Function to construct a series of libSBML objects for using FBC (constraint based) 
        """
        #mplugin = model.getPlugin('fbc') #this is the package for the contraint based modelling
        all_rp_models = {}
        for path_id in cofactors_rp_paths:
            sbmlns = libsbml.SBMLNamespaces(3,1,'fbc',1)
            try:
                #sbmlDoc = libsbml.SBMLDocument(3,1) #level, version
                sbmlDoc = libsbml.SBMLDocument(sbmlns)
            except ValueError:
                logging.error('Cannot create SBMLDocument object')
                return None 
            sbmlDoc.setPackageRequired('fbc', False)
            #Model
            model = sbmlDoc.createModel()
            self._checklibSBML(model, 'create model')
            #Compartments
            cytoplasm = model.createCompartment()
            self._checklibSBML(cytoplasm, 'create compartment')
            self._checklibSBML(cytoplasm.setId(compartment), 'set compartment id')
            self._checklibSBML(cytoplasm.setConstant(True), 'set compartment "constant"')
            self._checklibSBML(cytoplasm.setSize(1), 'set compartment "size"')
            self._checklibSBML(cytoplasm.setSBOTerm(290), 'set SBO term for the cytoplasm compartment')
            #Species
            new_meta = set([species for step_id in cofactors_rp_paths[path_id]['path'] for species in cofactors_rp_paths[path_id]['path'][step_id]['steps']])
            ##### TODO replace with list comprehension
            meta_smiles = {}
            for step_id in cofactors_rp_paths[path_id]['path']:
                for meta in cofactors_rp_paths[path_id]['path'][step_id]['steps']:
                    meta_smiles[meta] = cofactors_rp_paths[path_id]['path'][step_id]['steps'][meta]['smiles']
            new_meta = set([species for step_id in cofactors_rp_paths[path_id]['path'] for species in cofactors_rp_paths[path_id]['path'][step_id]['steps']])
            for meta in new_meta:
                spe = model.createSpecies()
                self._checklibSBML(spe, 'create species') 
                self._checklibSBML(spe.setCompartment(compartment), 'set species spe compartment')
                #ID same as cobrapy
                self._checklibSBML(spe.setId(self._nameToSbmlId(str(meta)+'__64__'+str(compartment))), 'set species id')
                self._checklibSBML(spe.setMetaId(self._nameToSbmlId('_'+md5(str(str(path_id)+'_'+meta).encode('utf-8')).hexdigest())), 'setting reaction metaID')
                #TODO: change this to the chemical name if known
                #self._checklibSBML(spe.setName(meta), 'set name for '+str(meta))
                ###### annotation ###
                if meta[:3]=='MNX':
                    annotation = '''<annotation>
                       <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:bqbiol="http://biomodels.net/biology-qualifiers/" xmlns:bqmodel="http://biomodels.net/model-qualifiers/">
                         <rdf:Description rdf:about="#'''+str(self._nameToSbmlId(meta))+'''">
                           <bqbiol:is>
                             <rdf:Bag>
                               <rdf:li rdf:resource="http://identifiers.org/metanetx.chemical/'''+str(meta)+'''"/>
                             </rdf:Bag>
                           </bqbiol:is>
                         </rdf:Description>
                       </rdf:RDF>
                     </annotation>'''
                    self._checklibSBML(spe.setAnnotation(annotation), 'setting the annotation for new reac') 
                else:
                    self._checklibSBML(spe.setNotes("<body xmlns='http://www.w3.org/1999/xhtml'><p>SMILES: "+str(meta_smiles[meta])+"</p></body>"), 'appending the SMILES notes for the reaction')
            #Reactions
            for step_id in cofactors_rp_paths[path_id]['path']:
                reac = model.createReaction()
                self._checklibSBML(reac, 'create reaction')
                self._checklibSBML(reac.setId('RP'+str(step_id)), 'set reaction id') #same convention as cobrapy
                self._checklibSBML(reac.setName('rpReaction_'+str(step_id)), 'set name') #same convention as cobrapy
                self._checklibSBML(reac.setSBOTerm(185), 'setting the system biology ontology (SBO)') #set as process
                self._checklibSBML(reac.setReversible(True), 'set reaction reversibility flag')
                self._checklibSBML(reac.setFast(False), 'set reaction "fast" attribute')
                #TODO: different files with the same step_id and path_id would have the same metaid --> check that its not a problem
                self._checklibSBML(reac.setMetaId(self._nameToSbmlId('_'+md5(str(str(path_id)+'_'+str(step_id)).encode('utf-8')).hexdigest())), 'setting species metaID')
                for meta in cofactors_rp_paths[path_id]['path'][step_id]['steps']: 
                    #### reactants ###
                    if float(cofactors_rp_paths[path_id]['path'][step_id]['steps'][meta]['stoichiometry'])<0:
                        spe_r = reac.createReactant()
                        self._checklibSBML(spe_r, 'create reactant')
                        self._checklibSBML(spe_r.setSpecies(str(meta)+'__64__'+str(compartment)), 'assign reactant species')
                        #self._checklibSBML(spe_r.setName(str(meta)+'_'+str(compartment)), 'assign reactant species')
                        self._checklibSBML(spe_r.setConstant(True), 'set "constant" on species '+str(meta))
                        self._checklibSBML(spe_r.setStoichiometry(abs(float(cofactors_rp_paths[path_id]['path'][step_id]['steps'][meta]['stoichiometry']))), 'set stoichiometry')
                    #### products ###
                    elif float(cofactors_rp_paths[path_id]['path'][step_id]['steps'][meta]['stoichiometry'])>0:
                        pro_r = reac.createProduct()
                        self._checklibSBML(pro_r, 'create product')
                        self._checklibSBML(pro_r.setSpecies(str(meta)+'__64__'+str(compartment)), 'assign product species')
                        #self._checklibSBML(pro_r.setName(str(meta)+'_'+str(compartment)), 'assign product species')
                        self._checklibSBML(pro_r.setConstant(True), 'set "constant" on species '+str(meta))
                        self._checklibSBML(pro_r.setStoichiometry(float(cofactors_rp_paths[path_id]['path'][step_id]['steps'][meta]['stoichiometry'])), 'set the stoichiometry')
                    else:
                        logging.error('The stoichiometry is 0 for path_id: '+str(path_id)+', step_id: '+str(step_id))
                #add the SMILES to the notes
                self._checklibSBML(reac.setNotes("<body xmlns='http://www.w3.org/1999/xhtml'><p>SMILES: "+str(cofactors_rp_paths[path_id]['path'][step_id]['smiles'])+"</p></body>"), 'appending the SMILES notes for the reaction')
            all_rp_models[path_id] = sbmlDoc
        if isExport:
            self._exportSBML('sbml_models', all_rp_models, 'libsbml', inPath)
        return all_rp_models



    #TODO: rewrite as a method that only exports the SBML from the retropath2.0 output
    def OLD_constructPaths_cobraPy(self, cofactors_rp_paths, ori_model_compartments, rp_smiles, isExport=False, inPath=None):
        """Construct the cobra models of the RetroPath paths with the cofactors and export them to SBML

            Assumes that all the reactions are happening in the cytoplasm
        """
        rp_sbml_paths = {}
        cytoplasm_compartment = [i for i in ori_model_compartments if ori_model_compartments[i]['short_name']=='c'][0] # this assuming that there is always only one result
        extracellular_compartment = [i for i in ori_model_compartments if ori_model_compartments[i]['short_name']=='e'][0] # this assuming that there is always only one result
        #NOTE: we assume that the metabolites are all in the cytoplasm (apart from the last transport step)
        #TODO: need to flag that the metabolites (sink) first step in the reaction is contained in the model - to validate the rp_path
        for path_id in cofactors_rp_paths:
            ########### METABOLITES #########################
            #create a new model where we will add this path to it
            model = cobra.Model(str(path_id))
            #new_meta=list(set([y for i in cofactors_rp_paths[path] for y in itertools.chain(i['right'], i['left'])]))
            new_meta = set([i for path_id in cofactors_rp_paths for step_id in cofactors_rp_paths[path_id]['path'] for i in cofactors_rp_paths[path_id]['path'][step_id]['steps'].keys()])
            all_meta = {}
            #enumerate all the unique compounds from a path
            for meta in new_meta:
                #remove the ones that already exist in the model
                if not meta in all_meta:
                    all_meta[meta] = cobra.Metabolite(meta, name=meta, compartment=cytoplasm_compartment)
                    #all_meta[meta].annotation = { 'ImaginaryCompDB':'SpecificCompIdentifier', "uniprot": ["Q12345", "P12345"]}
            ############## REACTIONS ##########################
            for step_id in cofactors_rp_paths[path_id]['path']:
                #TODO: could this lead to a conflict if there is the same reactionID and a different substrateID
                #reaction = cobra.Reaction(step['rule_id'].split('_')[0])
                reaction = cobra.Reaction('rpReaction_'+str(step_id))
                reaction.lower_bound = 0.0 # assume that all the reactions are irreversible
                reaction.upper_bound = 999999.0 #this is dependent on the fluxes of the others reactions
                reaction.gene_reaction_rule = 'RPGene_'+str(step_id)
                reac_meta = {}
                for mnxm in cofactors_rp_paths[path_id]['path'][step_id]['steps']:
                    reac_meta[all_meta[mnxm]] = float(cofactors_rp_paths[path_id]['path'][step_id]['steps'][mnxm]['stoichiometry'])
                reaction.add_metabolites(reac_meta)
                model.add_reactions([reaction])
            ################# Extracellular transport of target
            #NOTE: some molecules cannot be exported and thus this step should not be added
            #identify the target molecule
            target_name = [i for i in new_meta if i[:6]=='TARGET'][0]
            #create the metabolite for the extracellular version of the target metabolite
            extracell_target = cobra.Metabolite(target_name+'_e',
                                                name = target_name,
                                                compartment = extracellular_compartment)
            #Add the export from the cytoplasm to the extracellular matrix ######
            #exportReaction = cobra.Reaction('exportTarget')
            #exportReaction.name = 'ExportTarget'
            exportReaction = cobra.Reaction('targetSink')
            exportReaction.name = 'targetSink'
            exportReaction.lower_bound = 0.0 #default = 0.0
            exportReaction.upper_bound = 999999.0 #default = 1000 TODO: see if changing this changes something
            #these are the bounds for the yeast bigg model
            #TODO: check .reversibility of the reaction after setting these bounds
            #add that metabolite to the 
            #exportReaction.add_metabolites({extracell_target: 1.0, all_meta[target_name]: -1.0})
            exportReaction.add_metabolites({all_meta[target_name]: -1.0})
            #print(exportReaction.data_frame())  
            model.add_reactions([exportReaction])
            #rp_sbml_paths[path[0]['path_id']] = model
            rp_sbml_paths[path_id] = model
        if isExport:
            self._exportSBML('sbml_paths', rp_sbml_paths, 'cobrapy', inPath)
        return rp_sbml_paths

    ########################################################################
    ############################### FBA pathway ranking ####################
    ########################################################################

    #1) Number of interventions
    # need to calculate the number of steps that are not native to know the number of interventions

    #2) Maximal growth rate

    def simulateBiomass(self, cofactors_rp_path, model):
        #TODO: update the objective function here
        res = model.optimize()
        cofactors_rp_path['flux_biomass'] = res.fluxes['targetSink']
        for step_id in cofactors_rp_path['path']:
            cofactors_rp_path['path'][step_id]['flux_biomass'] = res.fluxes['rpReaction_'+str(step_id)]
        return True

    #3) Minimum product yeild at maximal growth rate

    #4) Minimum product yeild

    #5) Anaerobic condition

    #6) Number of potentially disruptive products

        #Toxicity?

    #7) Number of accessible metabolites (avoid intermediate accumulation)

    #8) Thermodynamics (MDF)

    #9) The overlap of the same changes --> might not be applicable in our case

    #10) Reduced model

    #11) ECM

    def simulateTarget(self, cofactors_rp_path, model):
        model.objective = 'targetSink'
        res = model.optimize()
        cofactors_rp_path['flux_target'] = res.fluxes['targetSink']
        for step_id in cofactors_rp_path['path']:
            cofactors_rp_path['path'][step_id]['flux_target'] = res.fluxes['rpReaction_'+str(step_id)]
        return True


    def simulateSplitObjective(self, cofactors_rp_path, model, ratio_biomass=0.5):
        if not 0.0<ratio_biomass<1.0:
            logging.error('The proportion of the objective that is given to BIOMASS must be 0.0< and 1.0>')
            return False
        model.objective = {model.reactions.R48E37591: ratio_biomass, 
                            model.reactions.targetSink: 1.0-ratio_biomass}
        res = model.optimize()
        cofactors_rp_path['flux_splitObj'] = res.fluxes['targetSink']
        for step_id in cofactors_rp_path['path']:
            cofactors_rp_path['path'][step_id]['flux_splitObj'] = res.fluxes['rpReaction_'+str(step_id)] 
        return True


    def simulateBiLevel(self, cofactors_rp_path, model):
        try:
            optknock = OptKnock(model, exclude_non_gene_reactions=False, remove_blocked=False)
            sim_res = optknock.run(max_knockouts=0, target='targetSink', biomass=self.biomassID)
            cofactors_rp_path['flux_biLevel'] = sim_res.fluxes[0]['targetSink']
        except KeyError:
            logging.error('KeyError with targetSink.... Not sure why that is')
            return False
        for step_id in cofactors_rp_path['path']:
            cofactors_rp_path['path'][step_id]['flux_biLevel'] = sim_res.fluxes[0]['rpReaction_'+str(step_id)]
        return True
