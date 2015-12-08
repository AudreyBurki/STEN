import wx
import Stat as Stat
import tables
import PostStat
import os
import time
import H5Tables
import numpy as np


class Start:

    """
    TODO: Description TEXT
    """

    def __init__(self, Mainframe):

        # Get relevant variables from Data and Analysis Panel
        self.PathResult = Mainframe.PanelData.TextResult.Value
        self.notebookSelected = Mainframe.PanelOption.GetSelection()
        self.H5 = Mainframe.H5
        self.Mainframe = Mainframe
        self.Cancel = False

        # ANOVA on Wave/GFP
        if self.notebookSelected == 0:
            self.AnovaCheck = self.Mainframe.AnovaWave.AnovaCheck
            self.AnovaAlpha = self.Mainframe.AnovaWave.Alpha
            self.AnovaClust = self.Mainframe.AnovaWave.Clust
            self.AnovaIteration = self.Mainframe.AnovaWave.nIteration
            self.AnovaParam = self.Mainframe.AnovaWave.Param
            self.AnovaPtsConsec = self.Mainframe.AnovaWave.PtsConseq
            self.PostHocCheck = self.Mainframe.AnovaWave.PostHocCheck
            self.PostHocAlpha = self.Mainframe.AnovaWave.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaWave.ClustPostHoc
            self.PostHocnIteration = self.Mainframe.AnovaWave.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaWave.ParamPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaWave.PtsConseqPostHoc
            self.SpaceFile = self.Mainframe.AnovaWave.SPIFile
            self.SPIPath = self.Mainframe.AnovaWave.SPIPath
            self.AnalyseType = self.Mainframe.AnovaWave.AnalyseType

        # ANOVA in Brain Space
        elif self.notebookSelected == 1:
            self.AnovaCheck = self.Mainframe.AnovaIS.AnovaCheck
            self.AnovaAlpha = self.Mainframe.AnovaIS.Alpha
            self.AnovaClust = self.Mainframe.AnovaIS.Clust
            self.AnovaIteration = self.Mainframe.AnovaIS.nIteration
            self.AnovaParam = self.Mainframe.AnovaIS.Param
            self.AnovaPtsConsec = self.Mainframe.AnovaIS.PtsConseq
            self.PostHocCheck = self.Mainframe.AnovaIS.PostHocCheck
            self.PostHocAlpha = self.Mainframe.AnovaIS.AlphaPostHoc
            self.PostHocClust = self.Mainframe.AnovaIS.ClustPostHoc
            self.PostHocnIteration = self.Mainframe.AnovaIS.nIterationPostHoc
            self.PostHocParam = self.Mainframe.AnovaIS.ParamPostHoc
            self.PostHocPtsConseq = self.Mainframe.AnovaIS.PtsConseqPostHoc
            self.SpaceFile = self.Mainframe.AnovaIS.SPIFile
            self.SPIPath = self.Mainframe.AnovaIS.SPIPath
            self.AnalyseType = None

        # Create result folder
        if not os.path.exists(self.PathResult):
            os.makedirs(self.PathResult)

        # Check which calculations were already computed
        self.checkForRerun()

        # Calculate ANOVA on Wave/GFP
        if self.notebookSelected == 0:
            self.calcAnovaWave()

        # Calculate ANOVA in Brain Space
        elif self.notebookSelected == 1:
            self.calcAnovaIS()

        # Write progressTxt to H5 file
        with tables.openFile(self.H5, mode='a') as h5file:

            # Delete previous content
            description = h5file.getNode('/Progress').description
            h5file.removeNode('/Progress', recursive=True)
            h5file.createTable('/', 'Progress', description)

            # Write new content
            progRow = h5file.getNode('/Progress').row
            for i, e in enumerate(self.progressTxt):
                progRow['Text']= e
                progRow.append()

        # TODO: Delete following line
        print 'DONE'

    def calcAnovaWave(self):

        # calcul Anova on wave and/or GFP
        if self.AnovaCheck:

            self.Wave = Stat.Anova(self.H5, self.Mainframe)

            # Parametric
            if self.AnovaParam:

                if self.AnalyseType in ["GFP Only", "Both"] and self.doAnovaParamGFP:
                    self.Wave.Param(DataGFP=True)
                    self.progressTxt.append('Parametric Anova (GFP) : %s' % self.Wave.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doAnovaParamElect:
                    self.Wave.Param()
                    self.progressTxt.append('Parametric Anova (All Electrodes) : %s' % self.Wave.elapsedTime)

            # Non Parametric
            else:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doAnovaNonParamGFP:
                    self.Wave.NonParam(self.AnovaIteration, DataGFP=True)
                    self.progressTxt.append('Non-Parametric Anova (GFP) : %s' % self.Wave.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doAnovaNonParamElect:
                    self.Wave.NonParam(self.AnovaIteration)
                    self.progressTxt.append('Non-Parametric Anova (All Electrodes) : %s' % self.Wave.elapsedTime)

            # TODO: Make sure that the h5 files are always closed at the end
            self.Wave.file.close()
            self.Cancel = self.Wave.Cancel

            # Post Stat (PostHoc) i.e Mathematical Morphology,
            # write Data
            # TODO: skip Post Stat (PostHoc) as long as PostStat.py is not updated
            #if not self.Cancel:
            if False:
                ResultName = 'Anova'
                PathResultAnova = os.path.abspath("/".join([self.PathResult, ResultName]))

                if not os.path.exists(PathResultAnova):
                    os.makedirs(PathResultAnova)

                if self.AnalyseType == "Both":
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=False, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=self.AnovaClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)

                    self.WavePostStat.file.close()
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=True, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=1, SpaceFile=None)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult, DataGFP=True)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()

                elif self.AnalyseType == "GFP Only":
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=True, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=1, SpaceFile=None)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult, DataGFP=True)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()
                elif self.AnalyseType == "All Electrodes":
                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=False, Param=self.AnovaParam)
                    self.WavePostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=self.AnovaClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultAnova)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results : %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteIntermediateResult(self.PathResult)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing intermediater EPH Results : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()


        # calcul PostHoc on wave and/or GFP
        if self.PostHocCheck:

            self.WavePostHoc = Stat.PostHoc(self.H5, self.Mainframe)

            # Parametric
            if self.PostHocParam:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doPostHocParamGFP:
                    self.WavePostHoc.Param(DataGFP=True)
                    self.progressTxt.append('Parametric PostHoc (GFP) : %s' % self.WavePostHoc.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doPostHocParamElect:
                    self.WavePostHoc.Param()
                    self.progressTxt.append('Parametric PostHoc (All Electrodes) : %s' % self.WavePostHoc.elapsedTime)

            # Non Parametric
            else:
                if self.AnalyseType in ["GFP Only", "Both"] and self.doPostHocNonParamGFP:
                    self.WavePostHoc.NonParam(self.PostHocIteration, DataGFP=True)
                    self.progressTxt.append('Non-Parametric PostHoc (GFP) : %s' % self.WavePostHoc.elapsedTime)

                if self.AnalyseType in ["All Electrodes", "Both"] and self.doPostHocNonParamElect:
                    self.WavePostHoc.NonParam(self.PostHocIteration)
                    self.progressTxt.append('Non-Parametric PostHoc (All Electrodes) : %s' % self.WavePostHoc.elapsedTime)

            # TODO: Make sure that the h5 files are always closed at the end
            self.WavePostHoc.file.close()
            self.Cancel = self.WavePostHoc.Cancel

            # Post Stat (PostHoc) i.e Mathematical Morphology, write
            # Data
            if not self.Cancel:
                ResultName = 'PostHoc'
                PathResultPostHoc = os.path.abspath("/".join([self.PathResult, ResultName]))

                if not os.path.exists(PathResultPostHoc):
                    os.makedirs(PathResultPostHoc)

                if self.AnalyseType == "Both":

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=False, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc(All electrodes) : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=True, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc(GFP) : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()

                elif self.AnalyseType == "GFP Only":

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=True, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (GFP): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc(GFP) : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()

                elif self.AnalyseType == "All Electrodes":

                    start = time.clock()
                    self.WavePostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=False, Param=self.PostHocParam)
                    self.WavePostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Multiple Test Correction on PostHoc (All electrodes): %s' % self.TimeTxt)

                    start = time.clock()
                    self.WavePostStat.WriteData(PathResultPostHoc)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append('Writing EPH Results on PostHoc : %s' % self.TimeTxt)
                    self.WavePostStat.file.close()



    def calcAnovaIS(self):

        # TODO: check for reruns

        if self.AnovaCheck:
            if CalculAnova:
                self.IS = Stat.Anova(self.H5, self)
                if self.AnovaParam:  # parametric
                    start = time.clock()
                    self.IS.Param()
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric Anova : ', self.TimeTxt]))
                    AllTime = self.IS.file.createArray('/Result/All', 'Anova_ElapsedTime', self.TimeTxt)

                else:  # non param
                    start = time.clock()
                    self.IS.NonParam(self.AnovaIteration)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Non-Parametric Anova : ', self.TimeTxt]))
                    AllTime = self.IS.file.createArray('/Result/All', 'Anova_ElapsedTime', self.TimeTxt)

                self.Cancel = self.IS.Cancel
                self.IS.file.close()

            # Post Stat (ANOVA) i.e Mathematical Morphology, write Data
            if not self.Cancel:
                ResultName = 'Anova'
                PathResultAnova = os.path.abspath( "/".join([PathResult, ResultName]))
                if not os.path.exists(PathResultAnova):
                    os.makedirs(PathResultAnova)
                start = time.clock()
                self.ISPostStat = PostStat.Data(self.H5, self, Anova=True, DataGFP=False, Param=self.AnovaParam)
                self.ISPostStat.MathematicalMorphology(self.AnovaAlpha, TF=self.AnovaPtsConsec, SpaceCriteria=self.AnovaClust, SpaceFile=self.SpaceFile)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Multiple Test Correction : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteData(PathResultAnova)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing EPH Results : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteIntermediateResult(PathResult)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing intermediater EPH Results : ', self.TimeTxt]))

                self.ISPostStat.file.close()

        # PostHoc on inverse space
        if self.PostHocCheck:
            if CalculPostHoc:
                self.ISPostHoc = Stat.PostHoc(self.H5, self)
                if self.PostHocParam:  # parametric
                    start = time.clock()
                    self.ISPostHoc.Param()
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric PostHoc : ', self.TimeTxt]))
                    AllTime = self.ISPostHoc.file.createArray('/Result/All', 'PostHoc_ElapsedTime', self.TimeTxt)
                else:  # Non param
                    start = time.clock()
                    self.ISPostHoc.NonParam(self.PostHocIteration)
                    end = time.clock()
                    elapsed = end - start
                    self.extractTime(elapsed)
                    self.progressTxt.append("".join(['Parametric PostHoc (All Electrodes) : ', self.TimeTxt]))
                    AllTime = self.ISPostHoc.file.createArray('/Result/All', 'PostHoc_ElapsedTime', self.TimeTxt)
                self.Cancel = self.ISPostHoc.Cancel
                self.ISPostStat.file.close()

            if not self.Cancel:
                ResultName = 'PostHoc'
                PathResultPostHoc = os.path.abspath("/".join([PathResult, ResultName]))

                if not os.path.exists(PathResultPostHoc):
                    os.makedirs(PathResultPostHoc)

                start = time.clock()
                self.ISPostStat = PostStat.Data(self.H5, self, Anova=False, DataGFP=False, Param=self.PostHocParam)
                self.ISPostStat.MathematicalMorphology(self.PostHocAlpha, TF=self.PostHocPtsConsec, SpaceCriteria=self.PostHocClust, SpaceFile=self.SpaceFile)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Multiple Test Correction on PostHoc : ', self.TimeTxt]))

                start = time.clock()
                self.ISPostStat.WriteData(PathResultPostHoc)
                end = time.clock()
                elapsed = end - start
                self.extractTime(elapsed)
                self.progressTxt.append("".join(['Writing EPH Results on PostHoc : ', self.TimeTxt]))
                self.ISPostStat.file.close()


    def checkIfCancel(self):

        # If cancel press
        if self.Cancel:
            file = tables.openFile(self.H5, 'r+')
            GFPDataTest = file.listNodes('/Result/GFP/Anova')
            AllDataTest = file.listNodes('/Result/All/Anova')
            if GFPDataTest != []:
                file.removeNode('/Result/GFP/Anova', recursive=True)
                file.createGroup('/Result/Anova', 'GFP')
            if AllDataTest != []:
                file.removeNode('/Result/All/Anova', recursive=True)
                file.createGroup('/Result/Anova', 'All')
            file.close()
            self.Mainframe.PanelData.TxtProgress.SetLabel("Calculation Cancel by user")
        else:
            self.Mainframe.PanelData.TxtProgress.SetLabel("\n".join(self.progressTxt))
            # self.writeVrb(self.H5, PathResult)
            dlg = wx.MessageDialog(self.Mainframe, style=wx.OK | wx.CANCEL, message='Work is done enjoy your results !!!! ;-)')
            retour = dlg.ShowModal()
            dlg.Destroy()
        

    def writeVrb(self, H5, ResultFolder):
        # ecrire le VRB
        file = tables.openFile(H5, 'r')
        Title = ['Analysis : \n']
        Param = ['Parameter :', '\n', '-----------', '\n']
        if self.AnovaCheck:
            # Anova
            Param.append('ANOVA :\n')
            Param.append('\tAlpha = ')
            Param.append(str(self.AnovaAlpha))
            Param.append('\n')
            Param.append('\tConsecutive Time Frame Criteria = ')
            Param.append(str(self.AnovaPtsConsec))
            Param.append('\n')

            if self.AnovaParam:
                if self.AnalyseType == "Both":
                    Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')
                    Title.append('\n')
                    Title.append('GFP Parametric Repeated Measure ANOVA across')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')

                    Param.append('\tCluster Criteria (Electrodes) = ')
                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')

                elif self.AnalyseType == "GFP Only":
                    Title.append('GFP Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/ShapeGFP')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                elif self.AnalyseType == "All Electrodes":
                    Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')
                    Param.append('\tCluster Criteria (Electrodes) = ')

                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
                elif self.AnalyseType is None:
                    Title.append('All electrodes Waveform Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Voxels')

                    Param.append('\tCluster Criteria (Voxels) = ')
                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
            else:
                if self.AnalyseType == "Both":
                    Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')
                    Title.append('\n')
                    Title.append('GFP Non-Parametric Repeated Measure ANOVA across')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')

                    Param.append('\tCluster Criteria (Electrodes) = ')
                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
                elif self.AnalyseType == "GFP Only":
                    Title.append('GFP Non-Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/ShapeGFP')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                elif self.AnalyseType == "All Electrodes":
                    Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')

                    Param.append('\tCluster Criteria (Electrodes) = ')
                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
                elif self.AnalyseType is None:
                    Title.append('All electrodes Waveform Non-Parametric Repeated Measure ANOVA across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Voxels')

                    Param.append('\tCluster Criteria (Voxels) = ')
                    Param.append(str(self.AnovaClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')

                Param.append('\tIteraction Value = ')
                Param.append(str(self.AnovaIteration))
                Param.append('\n')

        if self.AnovaCheck and self.PostHocCheck:
            Title.append('\n')
        if self.PostHocCheck:
            Param.append('Post-Hoc :\n')
            Param.append('\tAlpha = ')
            Param.append(str(self.PostHocAlpha))
            Param.append('\n')
            Param.append('\tConsecutive Time Frame Criteria = ')
            Param.append(str(self.PostHocPtsConsec))
            Param.append('\n')
            if self.PostHocParam:
                if self.AnalyseType == "Both":
                    Title.append('All electrodes Waveform Parametric POST-HOC across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frames and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')
                    Title.append('\n')
                    Title.append('GFP Parametric POST-HOC across')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frames')

                    Param.append('\tCluster Criteria (Electrodes) = ')
                    Param.append(str(self.PostHocClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')

                elif self.AnalyseType == "GFP Only":
                    Title.append('GFP Parametric POST-HOC across')
                    shape = file.getNode('/Info/ShapeGFP')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frames')
                elif self.AnalyseType == "All Electrodes":
                    Title.append('All electrodes Waveform Parametric POST-HOC across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frame and')
                    Title.append(str(shape.read()[1]))
                    Title.append('Electrodes')

                    Param.append('\tCluster Criteria (Electrodes) = ')
                    Param.append(str(self.PostHocClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
                elif self.AnalyseType is None:
                    Title.append('All electrodes Waveform Parametric POST-HOC across')
                    shape = file.getNode('/Info/Shape')
                    Title.append(str(shape.read()[0]))
                    Title.append('Time Frames and ')
                    Title.append(str(shape.read()[1]))
                    Title.append('Voxels')

                    Param.append('\tCluster Criteria (Voxels) = ')
                    Param.append(str(self.PostHocClust))
                    Param.append('\n')
                    Param.append('\tCluster Criteria (File) = ')
                    Param.append(str(self.SpaceFile))
                    Param.append('\n')
                else:
                    if self.AnalyseType == "Both":
                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                        shape = file.getNode('/Info/Shape')
                        Title.append(str(shape.read()[0]))
                        Title.append('Time Frames and')
                        Title.append(str(shape.read()[1]))
                        Title.append('Electrodes')
                        Title.append('\n')
                        Title.append('GFP Non-Parametric POST-HOC across')
                        Title.append(str(shape.read()[0]))
                        Title.append('Time Frames ')

                        Param.append('\tCluster Criteria (Electrodes) = ')
                        Param.append(str(self.PostHocClust))
                        Param.append('\n')
                        Param.append('\tCluster Criteria (File) = ')
                        Param.append(str(self.SpaceFile))
                        Param.append('\n')
                    elif self.AnalyseType == "GFP Only":
                        Title.append('GFP Non-Parametric POST-HOC across')
                        shape = file.getNode('/Info/ShapeGFP')
                        Title.append(str(shape.read()[0]))
                        Title.append('Time Frames')
                    elif self.AnalyseType == "All Electrodes":
                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                        shape = file.getNode('/Info/Shape')
                        Title.append(str(shape.read()[0]))
                        Title.append('Time Frames and')
                        Title.append(str(shape.read()[1]))
                        Title.append('Electrodes')

                        Param.append('\tCluster Criteria (Electrodes) = ')
                        Param.append(str(self.PostHocClust))
                        Param.append('\n')
                        Param.append('\tCluster Criteria (File) = ')
                        Param.append(str(self.SpaceFile))
                        Param.append('\n')
                    elif self.AnalyseType is None:
                        Title.append('All electrodes Waveform Non-Parametric POST-HOC across')
                        shape = file.getNode('/Info/Shape')
                        Title.append(str(shape.read()[0]))
                        Title.append('Time Frames and')
                        Title.append(str(shape.read()[1]))
                        Title.append('Voxels')

                        Param.append('\tCluster Criteria (Voxels) = ')
                        Param.append(str(self.PostHocClust))
                        Param.append('\n')
                        Param.append('\tCluster Criteria (File) = ')
                        Param.append(str(self.SpaceFile))
                        Param.append('\n')

        Factor = ['Factor Names and Levels :\n', '-------------------------\n']
        file.close()
        StatData = Stat.Anova(H5, self)
        Sheet = StatData.file.getNode('/Sheet/Value')
        InputFile = ['Input File in relation to factors :\n',
                     '-----------------------------------\n']
        Value = StatData.file.getNode('/Sheet/Value').read()
        ColWithin = StatData.file.getNode('/Info/ColWithin').read()
        ColFactor = StatData.file.getNode('/Info/ColFactor').read()
        if StatData.NameWithin:
            for i, w in enumerate(StatData.NameWithin):
                Factor.append('Within Subject Factor Name (Levels) :')
                InputFile.append('Within subject conditions :\n')
                if i == 0:
                    Factor.append(w)
                    Factor.append('(')
                    level = str(StatData.Within[:, i].max())
                    level = level[0:level.find('.')]
                    Factor.append(level)
                    Factor.append(')')
                else:
                    Factor.append(',')
                    Factor.append(w)
                    Factor.append('(')
                    level = str(StatData.Within[:, i].max())
                    level = level[0:level.find('.')]
                    Factor.append(level)
                    Factor.append(')')
            Factor.append('\n')
            Condition = []
            for f in ColFactor:
                tmp = []
                n = 0
                f = f[f.find('(') + 1:f.find(')')]
                for l in f:
                    if l.isdigit():
                        tmp.append('-')
                        tmp.append(StatData.NameWithin[n])
                        tmp.append(l)
                        n += 1
                tmp.remove('-')
                Condition.append("".join(tmp))
            for i, c in enumerate(Condition):
                InputFile.append('\t')
                InputFile.append(c)
                InputFile.append(' Condition Files :\n')
                Data = Value[ColWithin[i]]
                for f in Data:
                    InputFile.append('\t')
                    InputFile.append(f)
                    InputFile.append('\n')
                InputFile.append('\n')

        if StatData.NameBetween:
            Factor.append('Between Subject Factor Name (Levels) :')
            for i, b in enumerate(StatData.NameBetween):
                if i == 0:
                    Factor.append(b)
                    Factor.append('(')
                    try:
                        level = str(StatData.Between[:, i].max())
                    except:
                        level = str(StatData.Between.max())
                    level = level[0:level.find('.')]
                    Factor.append(level)
                    Factor.append(')')
                else:
                    Factor.append(',')
                    Factor.append(b)
                    Factor.append('(')
                    try:
                        level = str(StatData.Between[:, i].max())
                    except:
                        level = str(StatData.Between.max())
                    level = level[0:level.find('.')]
                    Factor.append(level)
                    Factor.append(')')
            Factor.append('\n')
            InputFile.append('Between subject conditions :\n')
            ColBetween = StatData.file.getNode('/Info/ColBetween').read()
            Condition = []
            for i, c in enumerate(ColBetween):
                Data = Value[c]
                for j, d in enumerate(Data):
                    text = [StatData.NameBetween[i]]
                    text.append(d)
                    text.append(':')
                    text = " ".join(text)
                    if Condition == []:
                        Condition.append('\t')
                        Condition.append(text)
                        Condition.append('\n')
                        Index = 1
                    else:
                        if Condition[Index] != text:
                            Condition.append('\n\t')
                            Condition.append(text)
                            Condition.append('\n')
                            Index = len(Condition) - 2

                    for w in ColWithin:
                        Condition.append('\t')
                        Condition.append(Value[w][j])
                        Condition.append('\n')
            InputFile.append("".join(Condition))
            InputFile.append('\n')
        if StatData.NameCovariate:

            Factor.append('Covariate Name :')
            for i, c in enumerate(StatData.NameCovariate):
                if i == 0:
                    Factor.append(c)
                else:
                    Factor.append(',')
                    Factor.append(c)
            Factor.append('\n')
            InputFile.append('Covariate Value(s) :\n')
            ColCovariate = StatData.file.getNode('/Info/ColCovariate').read()
            Condition = []
            for i, c in enumerate(ColCovariate):
                Condition.append('\t')
                Condition.append(StatData.NameCovariate[i])
                Condition.append('\n')
                Data = Value[c]
                for d in Data:
                    Condition.append('\t')
                    Condition.append(d)
                    Condition.append('\n')
            InputFile.append("".join(Condition))
        Title = " ".join(Title)
        Title = Title.split('\n')
        MaxLength = 0
        for p in Title:
            if len(p) > MaxLength:
                MaxLength = len(p)
        Mark = []
        for i in range(MaxLength):
            Mark.append('=')
        Mark.insert(0, '\t\t')
        Mark.append('\n')
        Title = "\n\t\t".join(Title)
        Param = "".join(Param)
        if StatData.NameCovariate:
            Title.replace('ANOVA', 'ANCOVA')
            Param.replace('ANOVA', 'ANCOVA')

        os.chdir(ResultFolder)
        VrbFile = open('info.vrb', "w")
        VrbFile.write("".join(Mark))
        VrbFile.write('\t\t')
        VrbFile.write(Title)
        VrbFile.write('\n')
        VrbFile.write("".join(Mark))
        VrbFile.write('\n')
        VrbFile.write(Param)
        VrbFile.write('\n')
        VrbFile.write(" ".join(Factor))
        VrbFile.write('\n')
        VrbFile.write("".join(InputFile))
        VrbFile.write('\n')
        VrbFile.close()
        file.close()
        StatData.file.close()

    def checkForRerun(self):

        h5file = tables.openFile(self.H5, mode='a')

        self.progressTxt = [e[0] for e in h5file.getNode('/Progress').read()]

        if self.progressTxt == []:
            self.progressTxt = ['Calculation Step :']

        self.doAnovaParamGFP = True
        self.doAnovaParamElect = True
        self.doAnovaNonParamGFP = True
        self.doAnovaNonParamElect = True
        self.doPostHocParamGFP = True
        self.doPostHocParamElect = True
        self.doPostHocNonParamGFP = True
        self.doPostHocNonParamElect = True

        calcMode = 'Parametric Anova (GFP)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doAnovaParamGFP = self.rerunMessage(h5file, calcMode)

        calcMode = 'Parametric Anova (All Electrodes)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doAnovaParamElect = self.rerunMessage(h5file, calcMode)

        calcMode = 'Non-Parametric Anova (GFP)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doAnovaNonParamGFP = self.rerunMessage(h5file, calcMode)

        calcMode = 'Non-Parametric Anova (All Electrodes)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doAnovaNonParamElect = self.rerunMessage(h5file, calcMode)

        calcMode = 'Parametric PostHoc (GFP)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doPostHocParamGFP = self.rerunMessage(h5file, calcMode)

        calcMode = 'Parametric PostHoc (All Electrodes)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doPostHocParamElect = self.rerunMessage(h5file, calcMode)

        calcMode = 'Non-Parametric PostHoc (GFP)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doPostHocNonParamGFP = self.rerunMessage(h5file, calcMode)

        calcMode = 'Non-Parametric PostHoc (All Electrodes)'
        if np.any([calcMode in p for p in self.progressTxt]):
            self.doPostHocNonParamElect = self.rerunMessage(h5file, calcMode)

        h5file.close()

    def rerunMessage(self, h5file, calcMode):

        progTxt = self.progressTxt[np.where(
            [calcMode in p for p in self.progressTxt])[0]]

        message = ['%s\nResults were already computed.\n\n' % progTxt,
                   'Do you want to recalculate them (YES) or \n',
                   'continue with the already computed results (NO)?']

        dlg = wx.MessageDialog(
            None, style=wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION,
            caption='%s already computed' % calcMode,
            message=''.join(message))
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer == wx.ID_YES:

            nodePath = '/Result'
            if 'All' in calcMode:
                nodePath += '/All'
            else:
                nodePath += '/GFP'
            if 'PostHoc' in calcMode:
                node = 'PostHoc'
            else:
                node = 'Anova'

            description = h5file.getNode(nodePath+'/'+node).description
            h5file.removeNode(nodePath+'/'+node, recursive=True)
            h5file.createTable(nodePath, node, description)

            # Delete progress Text from already computed step
            self.progressTxt.pop(np.where(np.asarray(self.progressTxt)==progTxt)[0])

            doRerun = True
        else:
            doRerun = False

        return doRerun
