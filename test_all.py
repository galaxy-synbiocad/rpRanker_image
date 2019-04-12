import pytest
import rpSBML
import libsbml


path_id = 1
steps = [{'right': {'CMPD_0000000003': 1, 'MNXM13': 1, 'MNXM15': 1, 'MNXM8': 1}, 'left': {'MNXM10': 1, 'MNXM188': 1, 'MNXM4': 1, 'MNXM1': 3}}, {'right': {'TARGET_0000000001': 1, 'MNXM1': 2}, 'left': {'CMPD_0000000003': 1, 'MNXM4': 1, }}]
reaction_smiles = ['[H]Oc1c([H])c([H])c([H])c([H])c1O[H]>>O=O.[H]N=C(O[H])C1=C([H])N(C2([H])OC([H])(C([H])([H])OP(=O)(O[H])OP(=O)(O[H])OC([H])([H])C3([H])OC([H])(n4c([H])nc5c(N([H])[H])nc([H])nc54)C([H])(O[H])C3([H])O[H])C([H])(O[H])C2([H])O[H])C([H])=C([H])C1([H])[H].[H]OC(=O)c1c([H])c([H])c([H])c([H])c1N([H])[H]', '[H]OC(=O)C([H])=C([H])C([H])=C([H])C(=O)O[H]>>O=O.[H]Oc1c([H])c([H])c([H])c([H])c1O[H]', ]
rp_smiles = {'MNXM10': '[H]N=C(O[H])C1=C([H])N(C2([H])OC([H])(C([H])([H])OP(=O)(O[H])OP(=O)(O[H])OC([H])([H])C3([H])OC([H])(n4c([H])nc5c(N([H])[H])nc([H])nc54)C([H])(O[H])C3([H])O[H])C([H])(O[H])C2([H])O[H])C([H])=C([H])C1([H])[H]',
'MNXM188': '[H]OC(=O)c1c([H])c([H])c([H])c([H])c1N([H])[H]',
'MNXM4': 'O=O',
'MNXM1': '[H+]',
'CMPD_0000000003': '[H]Oc1c([H])c([H])c([H])c([H])c1O[H]',
'MNXM13': 'O=C=O',
'MNXM15': '[H]N([H])[H]',
'MNXM8': 'NC(=O)c1ccc[n+](c1)[C@@H]1O[C@H](COP([O-])(=O)OP([O-])(=O)OC[C@H]2O[C@H]([C@H](O)[C@@H]2O)n2cnc3c(N)ncnc23)[C@@H](O)[C@H]1O',
'TARGET_0000000001': '[H]OC(=O)C([H])=C([H])C([H])=C([H])C(=O)O[H]'}
rp_inchi = {'MNXM10': 'InChI=1S/C21H29N7O14P2/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(32)14(30)11(41-21)6-39-44(36,37)42-43(34,35)38-5-10-13(29)15(31)20(40-10)27-3-1-2-9(4-27)18(23)33/h1,3-4,7-8,10-11,13-16,20-21,29-32H,2,5-6H2,(H2,23,33)(H,34,35)(H,36,37)(H2,22,24,25)/p-2/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1',
'MNXM188': 'InChI=1S/C7H7NO2/c8-6-4-2-1-3-5(6)7(9)10/h1-4H,8H2,(H,9,10)/p-1',
'MNXM4': 'InChI=1S/O2/c1-2',
'MNXM1': 'InChI=1S',
'CMPD_0000000003': None,
'MNXM13': 'InChI=1S/CO2/c2-1-3',
'MNXM15': 'InChI=1S/H3N/h1H3/p+1',
'MNXM8': 'InChI=1S/C21H27N7O14P2/c22-17-12-19(25-7-24-17)28(8-26-12)21-16(32)14(30)11(41-21)6-39-44(36,37)42-43(34,35)38-5-10-13(29)15(31)20(40-10)27-3-1-2-9(4-27)18(23)33/h1-4,7-8,10-11,13-16,20-21,29-32H,5-6H2,(H5-,22,23,24,25,33,34,35,36,37)/p-1/t10-,11-,13-,14-,15-,16-,20-,21-/m1/s1',
'TARGET_0000000001': 'InChI=1S/C6H6O4/c7-5(8)3-1-2-4-6(9)10/h1-4H,(H,7,8)(H,9,10)'}


class TestSBML(object):
    def createModel(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        inModel = libsbml.readSBML('models/test_createModel.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()


    def createUnitDefinition(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        unitDef = rpsbml.createUnitDefinition('mmol_per_gDW_per_hr')
        inModel = libsbml.readSBML('models/test_createUnitDefinition.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()


    def createUnit(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        unitDef = rpsbml.createUnitDefinition('mmol_per_gDW_per_hr')
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_MOLE, 1, -3, 1)
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_GRAM, 1, 0, 1)
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_SECOND, 1, 0, 3600)
        inModel = libsbml.readSBML('models/test_createUnit.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()


    def createParameter(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        upInfParam = rpsbml.createParameter('B_INF', float('inf'), 'kj_per_mol')
        inModel = libsbml.readSBML('models/test_createParameter.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()


    def createCompartent(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        rpsbml.createCompartment(1, 'cytoplasm')
        inModel = libsbml.readSBML('models/test_createCompartment.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()
        

    def genericModel(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        inModel = libsbml.readSBML('models/test_genericModel.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()


    def createSpecies(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm', 0, '', None, None)
        inModel = libsbml.readSBML('models/test_createSpecies.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()  


    def createPathway(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm')
        rpsbml.createPathway(path_id)
        inModel = libsbml.readSBML('models/test_createPathway.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()  


    def createReaction(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm')
        rpsbml.createPathway(path_id)
        #reactions
        step_id = 0
        for stepNum in range(len(steps)):
            rpsbml.createReaction('RP_'+str(stepNum), 'B_INF', 'B__INF', steps[stepNum], reaction_smiles[stepNum], 'cytoplasm')
            step_id += 1
        inModel = libsbml.readSBML('models/test_createReaction.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()  
        

    def createFluxObj(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm')
        rpsbml.createPathway(path_id)
        step_id = 0
        for stepNum in range(len(steps)):
            rpsbml.createReaction('RP_'+str(stepNum), 'B_INF', 'B__INF', steps[stepNum], reaction_smiles[stepNum], 'cytoplasm')
            step_id += 1
        rpsbml.createFluxObj('flux1', 'RP_1', 2.0, True)
        inModel = libsbml.readSBML('models/test_createReaction.sbml')
        assert inModel.toSBML()==rpsbml.document.toSBML()  


    def readSBML(self):
        rpsbml = rpSBML.rpSBML()
        document, model, errors = rpsbml._readSBML('models/test_genericModel.sbml')     
        inModel = libsbml.readSBML('models/test_createReaction.sbml')
        assert document.toSBML()==inModel.toSBML()


    def writeSBML(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        rpsbml._writeSBML('test_writeSBML.sbml', 'models') 
        inModel = libsbml.readSBML('models/test_writeSBML.sbml')
        assert rpsbml.document.toSBML()==inModel.toSBML() 


    #not sure how to test this function - perhaps throw an error at it
    #def checklibSBML(self):

    def nameToSbmlId(self):
        rpsbml = rpSBML.rpSBML()
        id_name = rpsbml._nameToSbmlId('###test_input-23####')
        assert id_name=='___test_input_23___'


    def genMetaID(self):
        rpsbml = rpSBML.rpSBML()
        id_name = rpsbml._genMetaID('###test_input-23####')
        assert id_name=='_5df40e51a5d358ecfdf0372317853a79'


    def readAnnotation(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm', 0, '', None, None)
        annot = rpsbml.readAnnotation(rpsbml.model.getSpecies('MNXM1__64__cytoplasm').getAnnotation())
        assert annot=={'bigg.metabolite': ['h', 'M_h'],
                'metanetx.chemical': ['MNXM1', 'MNXM145872', 'MNXM89553'],
                'chebi': ['CHEBI:15378', 'CHEBI:10744', 'CHEBI:13357', 'CHEBI:5584'],
                'hmdb': ['HMDB59597'],
                'kegg.compound': ['C00080'],
                'seed.compound': ['cpd00067']}
        

    def readIBISBAAnnotation(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm', 0, '', None, None)
        rpsbml.createPathway(path_id)
        #reactions
        step_id = 0
        for stepNum in range(len(steps)):
            rpsbml.createReaction('RP_'+str(stepNum), 'B_INF', 'B__INF', steps[stepNum], reaction_smiles[stepNum], 'cytoplasm', None, None)
            step_id += 1
        assert rpsbml.readIBISBAAnnotation(rpsbml.model.getSpecies('MNXM1__64__cytoplasm').getAnnotation())=={'smiles': '[H+]', 'inchi': 'InChI=1S', 'inchikey': '', 'ddG': {'units': 'kj_per_mol', 'value': ''}, 'ddG_uncert': {'units': 'kj_per_mol', 'value': ''}}


    def compareAnnotations(self):
        


    def mergeModels(self):






class genTestFiles():
    def __init__(self, outputPath):
        self.ouputPath = outputPath


    def createModel(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createModel.sbml')


    def createUnitDefinition(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        unitDef = rpsbml.createUnitDefinition('mmol_per_gDW_per_hr')
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createUnitDefinition.sbml')


    def createUnit(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        unitDef = rpsbml.createUnitDefinition('mmol_per_gDW_per_hr')
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_MOLE, 1, -3, 1)
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_GRAM, 1, 0, 1)
        rpsbml.createUnit(unitDef, libsbml.UNIT_KIND_SECOND, 1, 0, 3600)
        libsbml.writeSBML(rpsbml.document, self.ouputPath+'test_createUnit.sbml')

        
    def createParameter(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        upInfParam = rpsbml.createParameter('B_INF', float('inf'), 'kj_per_mol')
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createParameter.sbml')


    def createCompartent(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.createModel('RetroPath_heterologous_pathway', 'rp_model')
        rpsbml.createCompartment(1, 'cytoplasm')
        libsbml.writeSBML(rpsbml.document, self.ouputPath+'test_createCompartent.sbml')


    def genericModel(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_genericModel.sbml')


    def createSpecies(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm', 0, '', None, None)
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createSpecies.sbml')


    def createPathway(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm', 0, '', None, None)
        rpsbml.createPathway(path_id)
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createPathway.sbml')


    def createReaction(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm')
        rpsbml.createPathway(path_id)
        #reactions
        step_id = 0
        for stepNum in range(len(steps)):
            rpsbml.createReaction('RP_'+str(stepNum), 'B_INF', 'B__INF', steps[stepNum], reaction_smiles[stepNum], 'cytoplasm', None, None)
            step_id += 1
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createReaction.sbml')


    def createFluxObj(self):
        rpsbml = rpSBML.rpSBML()
        rpsbml.genericModel('RetroPath_heterologous_pathway', 'rp_model')
        for meta in set([i for step in steps for lr in ['left', 'right'] for i in step[lr]]):
            try:
                inchi = rp_inchi[meta]
            except KeyError:
                inchi = None
            try:
                smiles = rp_smiles[meta]
            except KeyError:
                smiles = None
            rpsbml.createSpecies(meta, None, inchi, smiles, 'cytoplasm')
        rpsbml.createPathway(path_id)
        step_id = 0
        for stepNum in range(len(steps)):
            rpsbml.createReaction('RP_'+str(stepNum), 'B_INF', 'B__INF', steps[stepNum], reaction_smiles[stepNum], 'cytoplasm', None, None)
            step_id += 1
        rpsbml.createFluxObj('flux1', 'RP_1', 2.0, True)
        libsbml.writeSBML(rpsbml.document, self.outputPath+'test_createFluxObj.sbml')


        
