# SRF
SRF Development (Sub-Regional Forecasting System)

Step 1: Contact the administrator to set up database user and modify the PostgreSQL connection information in dbparams.yaml. 

Step 2: Update machine_settings.py based on your computer's setting such as the path to java run command.

Step 3: Go to directory PECAS/AllYears and make directory "Code" here
        Copy the *.jar files and hdf5 folder from the current PECAS model AllYears/Code folder.
        The current PECAS model can be checked out from the following url:
        https://svn.hbaspecto.com/svn/pecas/PECASSanDiego/S21u_m
        
        Also check to make sure aa.properties is in the AllYears/Inputs folder. If not, you will get aa bundle not found error. 

Step 4: Create an empty file Outputsamples_sandag.csv in AllYears\Working\PopulationSynthesis directory.

Step 5: Run aa only model for all years by: 
        cd PECAS/S21u_m_aa
        python run_aa_allyears.py 

Step 6: Run MU Land Supply Model by:
        cd Supply/REDM
        python redm_main.py
        
        
Step 7: Run MU Land Demand Model by:
        cd E:\PECAS\SRF\trunk\Demand
        "C:\Program Files\R\R-4.0.2\bin\R.exe" CMD BATCH .\R\evalDemand.R
        or 
        "C:\Program Files\R\R-4.0.2\bin\Rscript.exe" .\R\evalDemand.
         Make sure the path to R command or Rscript command is correct.
   




