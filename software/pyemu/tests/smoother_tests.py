import os
if not os.path.exists("temp"):
    os.mkdir("temp")

def henry_setup():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("smoother","henry_pc","pest.pst"))
    par = pst.parameter_data
    par.loc[:,"parlbnd"] = 20.0
    par.loc[:,"parubnd"] = 2000.0
    par.loc["mult1","parlbnd"] = 0.9
    par.loc["mult1","parubnd"] = 1.1

    # obs = pst.observation_data
    # head_groups = obs.groupby(obs.apply(lambda x: x.obgnme=="head" and x.weight>0.0, axis=1)).groups[True]
    # obs.loc[head_groups,"weight"] = 1.0
    # conc_groups = obs.groupby(obs.apply(lambda x: x.obgnme=="conc" and x.weight>0.0, axis=1)).groups[True]
    # obs.loc[conc_groups,"weight"] = 0.5

    pst.pestpp_options["sweep_parameter_csv_file"] = "sweep_in.csv"
    pst.write(pst.filename.replace("pest.pst","henry.pst"))


def henry():
    import os
    import pyemu
    os.chdir(os.path.join("smoother", "henry_pc"))
    csv_files = [f for f in os.listdir('.') if f.endswith(".csv")]
    [os.remove(csv_file) for csv_file in csv_files]
    pst = pyemu.Pst(os.path.join("henry.pst"))
    es = pyemu.EnsembleSmoother(pst, num_slaves=15, use_approx=True)
    es.initialize(210, init_lambda=1.0)
    for i in range(10):
        es.update(lambda_mults=[0.2,5.0],run_subset=45)
    os.chdir(os.path.join("..", ".."))


def henry_plot():
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    import pandas as pd
    from pyemu import Pst
    d = os.path.join("smoother","henry_pc")
    pst = Pst(os.path.join(d,"henry.pst"))
    plt_dir = os.path.join(d,"plot")
    if not os.path.exists(plt_dir):
        os.mkdir(plt_dir)

    par_files = [os.path.join(d,f) for f in os.listdir(d) if "parensemble." in f
                 and ".png" not in f]
    par_dfs = [pd.read_csv(par_file,index_col=0).apply(np.log10) for par_file in par_files]
    par_names = ["mult1"]
    mx = (pst.parameter_data.loc[:,"parubnd"] * 1.1).apply(np.log10)
    mn = (pst.parameter_data.loc[:,"parlbnd"] * 0.9).apply(np.log10)

    obj_df = pd.read_csv(os.path.join(d,"henry.pst.iobj.csv"),index_col=0)
    real_cols = [col for col in obj_df.columns if col.startswith("0")]
    obj_df.loc[:,real_cols] = obj_df.loc[:,real_cols].apply(np.log10)
    obj_df.loc[:,"mean"] = obj_df.loc[:,"mean"].apply(np.log10)
    obj_df.loc[:, "std"] = obj_df.loc[:, "std"].apply(np.log10)

    fig = plt.figure(figsize=(20, 10))
    ax = plt.subplot(111)
    axt = plt.twinx()
    obj_df.loc[:, real_cols].plot(ax=ax, lw=0.5, color="0.5", alpha=0.5, legend=False)
    ax.plot(obj_df.index, obj_df.loc[:, "mean"], 'b', lw=2.5,marker='.',markersize=5)
    #ax.fill_between(obj_df.index, obj_df.loc[:, "mean"] - (1.96 * obj_df.loc[:, "std"]),
    #                obj_df.loc[:, "mean"] + (1.96 * obj_df.loc[:, "std"]),
    #                facecolor="b", edgecolor="none", alpha=0.25)
    axt.plot(obj_df.index,obj_df.loc[:,"lambda"],"k",dashes=(2,1),lw=2.5)
    ax.set_ylabel("log$_10$ phi")
    axt.set_ylabel("lambda")
    ax.set_title("total runs:{0}".format(obj_df.total_runs.max()))
    plt.savefig(os.path.join(plt_dir,"iobj.pdf"))
    plt.close()

    with PdfPages(os.path.join(plt_dir,"parensemble.pdf")) as pdf:

        for par_file,par_df in zip(par_files,par_dfs):
            print(par_file)
            fig = plt.figure(figsize=(20,10))

            plt.figtext(0.5,0.975,par_file,ha="center")
            axes = [plt.subplot(1,1,i+1) for i in range(len(par_names))]
            for par_name,ax in zip(par_names,axes):
                mean = par_df.loc[:,par_name].mean()
                std = par_df.loc[:,par_name].std()
                par_df.loc[:,par_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.5,grid=False)
                ax.set_yticklabels([])
                ax.set_title("{0}, {1:6.2f}".\
                             format(par_name,10.0**mean))
                ax.set_xlim(mn[par_name],mx[par_name])
                ylim = ax.get_ylim()
                if "mult1" in par_name:
                    val = np.log10(1.0)
                else:
                    val = np.log10(200.0)
                ticks = ["{0:2.1f}".format(x) for x in 10.0**ax.get_xticks()]
                ax.set_xticklabels(ticks,rotation=90)
                ax.plot([val,val],ylim,"k-",lw=2.0)

                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
            pdf.savefig()
            plt.close()




    obs_files = [os.path.join(d,f) for f in os.listdir(d) if "obsensemble." in f
                 and ".png" not in f]
    obs_dfs = [pd.read_csv(obs_file) for obs_file in obs_files]
    #print(obs_files)
    #mx = max([obs_df.obs.max() for obs_df in obs_dfs])
    #mn = min([obs_df.obs.min() for obs_df in obs_dfs])
    #print(mn,mx)
    obs_names = pst.nnz_obs_names
    obs_names.extend(["pd_one","pd_ten","pd_half"])
    print(len(obs_names))
    #print(obs_files)
    obs_dfs = [obs_df.loc[:,obs_names] for obs_df in obs_dfs]
    mx = {obs_name:max([obs_df.loc[:,obs_name].max() for obs_df in obs_dfs]) for obs_name in obs_names}
    mn = {obs_name:min([obs_df.loc[:,obs_name].min() for obs_df in obs_dfs]) for obs_name in obs_names}

    with PdfPages(os.path.join(plt_dir,"obsensemble.pdf")) as pdf:
        for obs_file,obs_df in zip(obs_files,obs_dfs):
            fig = plt.figure(figsize=(30,20))
            plt.figtext(0.5,0.975,obs_file,ha="center")
            print(obs_file)
            axes = [plt.subplot(8,5,i+1) for i in range(len(obs_names))]
            for ax,obs_name in zip(axes,obs_names):
                mean = obs_df.loc[:,obs_name].mean()
                std = obs_df.loc[:,obs_name].std()
                obs_df.loc[:,obs_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.5,grid=False)
                ax.set_yticklabels([])
                #print(ax.get_xlim(),mn[obs_name],mx[obs_name])
                ax.set_title("{0}, {1:6.2f}:{2:6.2f}".format(obs_name,mean,std))
                ax.set_xlim(mn[obs_name],mx[obs_name])
                #ax.set_xlim(0.0,20.0)
                ylim = ax.get_ylim()
                oval = pst.observation_data.loc[obs_name,"obsval"]
                ax.plot([oval,oval],ylim,"k-",lw=2)
                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
                ax.set_xticklabels([])
            pdf.savefig()
            plt.close()


def freyberg():
    import os
    import pyemu

    os.chdir(os.path.join("smoother","freyberg"))
    csv_files = [f for f in os.listdir('.') if f.endswith(".csv")]
    [os.remove(csv_file) for csv_file in csv_files]

    pst = pyemu.Pst(os.path.join("freyberg.pst"))

    es = pyemu.EnsembleSmoother(pst,num_slaves=20,use_approx=True)

    es.initialize(300,init_lambda=5000.0)
    for i in range(10):
        es.update(lambda_mults=[0.2,5.0],run_subset=40)
    os.chdir(os.path.join("..",".."))

def freyberg_plot():
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import pandas as pd
    from pyemu import Pst
    d = os.path.join("smoother","freyberg")
    pst = Pst(os.path.join(d,"freyberg.pst"))
    plt_dir = os.path.join(d,"plot")
    if not os.path.exists(plt_dir):
        os.mkdir(plt_dir)

    obs_files = [os.path.join(d,f) for f in os.listdir(d) if "obsensemble." in f
                 and ".png" not in f]
    obs_dfs = [pd.read_csv(obs_file) for obs_file in obs_files]
    obs_names = pst.nnz_obs_names
    obs_names.extend(pst.pestpp_options["forecasts"].split(',')[:-1])
    print(obs_names)
    print(len(obs_names))
    #print(obs_files)
    obs_dfs = [obs_df.loc[:,obs_names] for obs_df in obs_dfs]
    mx = {obs_name:max([obs_df.loc[:,obs_name].max() for obs_df in obs_dfs]) for obs_name in obs_names}
    mn = {obs_name:min([obs_df.loc[:,obs_name].min() for obs_df in obs_dfs]) for obs_name in obs_names}

    obj_df = pd.read_csv(os.path.join(d, "freyberg.pst.iobj.csv"), index_col=0)
    real_cols = [col for col in obj_df.columns if col.startswith("0")]
    obj_df.loc[:, real_cols] = obj_df.loc[:, real_cols].apply(np.log10)
    obj_df.loc[:, "mean"] = obj_df.loc[:, "mean"].apply(np.log10)
    obj_df.loc[:, "std"] = obj_df.loc[:, "std"].apply(np.log10)

    fig = plt.figure(figsize=(20, 10))
    ax = plt.subplot(111)
    axt = plt.twinx()
    obj_df.loc[:, real_cols].plot(ax=ax, lw=0.5, color="0.5", alpha=0.5, legend=False)
    ax.plot(obj_df.index, obj_df.loc[:, "mean"], 'b', lw=2.5, marker='.', markersize=5)
    # ax.fill_between(obj_df.index, obj_df.loc[:, "mean"] - (1.96 * obj_df.loc[:, "std"]),
    #                obj_df.loc[:, "mean"] + (1.96 * obj_df.loc[:, "std"]),
    #                facecolor="b", edgecolor="none", alpha=0.25)
    axt.plot(obj_df.index, obj_df.loc[:, "lambda"], "k", dashes=(2, 1), lw=2.5)
    ax.set_ylabel("log$_10$ phi")
    axt.set_ylabel("lambda")
    ax.set_title("total runs:{0}".format(obj_df.total_runs.max()))
    plt.savefig(os.path.join(plt_dir, "iobj.pdf"))
    plt.close()

    with PdfPages(os.path.join(plt_dir,"obsensemble.pdf")) as pdf:
        for obs_file,obs_df in zip(obs_files,obs_dfs):
            fig = plt.figure(figsize=(30,40))
            plt.figtext(0.5,0.975,obs_file,ha="center")
            print(obs_file)
            axes = [plt.subplot(3,4,i+1) for i in range(len(obs_names))]
            for ax,obs_name in zip(axes,obs_names):
                mean = obs_df.loc[:,obs_name].mean()
                std = obs_df.loc[:,obs_name].std()
                obs_df.loc[:,obs_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.25,grid=False)
                ax.set_yticklabels([])
                #print(ax.get_xlim(),mn[obs_name],mx[obs_name])
                ax.set_title("{0}, {1:6.2f}:{2:6.2f}".format(obs_name,mean,std))
                ax.set_xlim(mn[obs_name],mx[obs_name])
                #ax.set_xlim(0.0,20.0)
                ylim = ax.get_ylim()
                oval = pst.observation_data.loc[obs_name,"obsval"]
                ax.plot([oval,oval],ylim,"k-",lw=2)
                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
            pdf.savefig()
            plt.close()

    par_files = [os.path.join(d,f) for f in os.listdir(d) if "parensemble." in f
                 and ".png" not in f]
    par_dfs = [pd.read_csv(par_file,index_col=0).apply(np.log10) for par_file in par_files]
    #par_names = list(par_dfs[0].columns)
    par_names = ["rch_1","rch_2"]
    mx = (pst.parameter_data.loc[:,"parubnd"] * 1.1).apply(np.log10)
    mn = (pst.parameter_data.loc[:,"parlbnd"] * 0.9).apply(np.log10)

    with PdfPages(os.path.join(plt_dir,"parensemble.pdf")) as pdf:
        for par_file,par_df in zip(par_files,par_dfs):
            print(par_file)
            fig = plt.figure(figsize=(20,10))

            plt.figtext(0.5,0.975,par_file,ha="center")
            axes = [plt.subplot(2,6,i+1) for i in range(len(par_names))]
            for par_name,ax in zip(par_names,axes):
                mean = par_df.loc[:,par_name].mean()
                std = par_df.loc[:,par_name].std()
                par_df.loc[:,par_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.25,grid=False)
                ax.set_yticklabels([])
                ax.set_title("{0}, {1:6.2f}".\
                             format(par_name,10.0**mean))
                ax.set_xlim(mn[par_name],mx[par_name])
                ylim = ax.get_ylim()
                if "stage" in par_name:
                    val = np.log10(1.5)
                else:
                    val = np.log10(2.5)
                ticks = ["{0:2.1f}".format(x) for x in 10.0**ax.get_xticks()]
                ax.set_xticklabels(ticks,rotation=90)
                ax.plot([val,val],ylim,"k-",lw=2.0)

                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
            pdf.savefig()
            plt.close()

def chenoliver_setup():
    import pyemu
    os.chdir(os.path.join("smoother","chenoliver"))
    in_file = os.path.join("par.dat")
    tpl_file = in_file+".tpl"
    out_file = os.path.join("obs.dat")
    ins_file = out_file+".ins"
    pst = pyemu.pst_utils.pst_from_io_files(tpl_file,in_file,ins_file,out_file)
    par = pst.parameter_data
    par.loc[:,"partrans"] = "none"
    par.loc[:,"parval1"] = 10.0
    par.loc[:,"parubnd"] = -1.0
    par.loc[:,"parlbnd"] = -10.0
    obs = pst.observation_data
    obs.loc[:,"obsval"] = 48.0
    obs.loc[:,"weight"] = 1.0
    pst.model_command = ["python chenoliver.py"]
    pst.control_data.noptmax = 0
    pst.pestpp_options["sweep_parameter_csv_file"] = os.path.join("sweep_in.csv")
    pst.write(os.path.join("chenoliver.pst"))

    os.chdir(os.path.join("..",".."))

def chenoliver_plot():
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    import pandas as pd
    d = os.path.join("smoother","chenoliver")
    bins = 20
    plt_dir = os.path.join(d,"plot")
    if not os.path.exists(plt_dir):
        os.mkdir(plt_dir)
    obs_files = [os.path.join(d,f) for f in os.listdir(d) if "obsensemble." in f
                 and ".png" not in f]
    obs_dfs = [pd.read_csv(obs_file) for obs_file in obs_files]
    #print(obs_files)
    mx = max([obs_df.obs.max() for obs_df in obs_dfs])
    mn = min([obs_df.obs.min() for obs_df in obs_dfs])
    #print(mn,mx)
    with PdfPages(os.path.join(plt_dir,"obsensemble.pdf")) as pdf:
        for obs_file,obs_df in zip(obs_files,obs_dfs):
            #fig = plt.figure(figsize=(10,10))
            ax = plt.subplot(111)
            obs_df.loc[:,["obs"]].hist(ax=ax,bins=bins,edgecolor="none")
            ax.set_xlim(mn,mx)
            ax.set_title("{0}".format(obs_file))
            #plt.savefig(os.path.join(plt_dir,os.path.split(obs_file)[-1]+".png"))
            #plt.close("all")
            pdf.savefig()
            plt.close()

    par_files = [os.path.join(d,f) for f in os.listdir(d) if "parensemble." in f
                 and ".png" not in f]
    par_dfs = [pd.read_csv(par_file) for par_file in par_files]
    #mx = max([par_df.par.max() for par_df in par_dfs])
    #mn = min([par_df.par.min() for par_df in par_dfs])
    mx = 7
    mn = -5

    with PdfPages(os.path.join(plt_dir,"parensemble.pdf")) as pdf:
        for par_file in par_files:
            par_df = pd.read_csv(par_file)
            fig = plt.figure(figsize=(10,10))
            ax = plt.subplot(111)
            par_df.loc[:,["par"]].hist(ax=ax,bins=bins,edgecolor="none")
            #ax.set_xlim(-10,10)
            ax.set_xlim(mn,mx)

            ax.set_xticks(np.arange(mn,mx+0.25,0.25))
            ax.set_xticklabels(["{0:2.2f}".format(x) for x in np.arange(mn,mx+0.25,0.25)], rotation=90)
            ax.set_title("{0}".format(par_file))
            #plt.savefig(os.path.join(plt_dir,os.path.split(par_file)[-1]+".png"))
            #plt.close("all")
            pdf.savefig()
            plt.close()

def chenoliver():
    import os
    import numpy as np
    import pyemu

    os.chdir(os.path.join("smoother","chenoliver"))
    csv_files = [f for f in os.listdir('.') if f.endswith(".csv") and "bak" not in f]
    [os.remove(csv_file) for csv_file in csv_files]

    parcov = pyemu.Cov(x=np.ones((1,1)),names=["par"],isdiagonal=True)
    pst = pyemu.Pst("chenoliver.pst")
    obscov = pyemu.Cov(x=np.ones((1,1))*16.0,names=["obs"],isdiagonal=True)
    es = pyemu.EnsembleSmoother(pst,parcov=parcov,obscov=obscov,
                                num_slaves=20,use_approx=False)
    es.initialize(num_reals=100)
    for it in range(40):
        es.update()
    os.chdir(os.path.join("..",".."))

def tenpar():
    import os
    import numpy as np
    import pyemu
    os.chdir(os.path.join("smoother","10par_xsec"))
    csv_files = [f for f in os.listdir('.') if f.endswith(".csv")]
    [os.remove(csv_file) for csv_file in csv_files]
    es = pyemu.EnsembleSmoother("10par_xsec.pst",num_slaves=5,use_approx=True)
    lz = es.get_localizer().to_dataframe()
    #the k pars upgrad of h01_04 and h01_06 are localized
    upgrad_pars = [pname for pname in lz.columns if "_" in pname and\
                   int(pname.split('_')[1]) > 4]
    lz.loc["h01_04",upgrad_pars] = 0.0
    upgrad_pars = [pname for pname in lz.columns if '_' in pname and \
                   int(pname.split('_')[1]) > 6]
    lz.loc["h01_06", upgrad_pars] = 0.0
    lz = pyemu.Matrix.from_dataframe(lz).T
    print(lz)
    es.initialize(num_reals=20)

    for it in range(20):
        es.update(lambda_mults=[0.1,1.0,10.0])#,localizer=lz,run_subset=20)
        #es.update(lambda_mults=[1.0])
    os.chdir(os.path.join("..",".."))

def tenpar_plot():
    import os
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    import pandas as pd
    from pyemu import Pst
    d = os.path.join("smoother","10par_xsec")
    pst = Pst(os.path.join(d,"10par_xsec.pst"))
    plt_dir = os.path.join(d,"plot")
    if not os.path.exists(plt_dir):
        os.mkdir(plt_dir)


    par_files = [os.path.join(d,f) for f in os.listdir(d) if "parensemble." in f
                 and ".png" not in f]
    par_dfs = [pd.read_csv(par_file,index_col=0).apply(np.log10) for par_file in par_files]
    par_names = list(par_dfs[0].columns)
    mx = (pst.parameter_data.loc[:,"parubnd"] * 1.1).apply(np.log10)
    mn = (pst.parameter_data.loc[:,"parlbnd"] * 0.9).apply(np.log10)

    obj_df = pd.read_csv(os.path.join(d,"10par_xsec.pst.iobj.csv"),index_col=0)
    real_cols = [col for col in obj_df.columns if col.startswith("0")]
    obj_df.loc[:,real_cols] = obj_df.loc[:,real_cols].apply(np.log10)
    obj_df.loc[:,"mean"] = obj_df.loc[:,"mean"].apply(np.log10)
    obj_df.loc[:, "std"] = obj_df.loc[:, "std"].apply(np.log10)

    fig = plt.figure(figsize=(20, 10))
    ax = plt.subplot(111)
    axt = plt.twinx()
    obj_df.loc[:, real_cols].plot(ax=ax, lw=0.5, color="0.5", alpha=0.5, legend=False)
    ax.plot(obj_df.index, obj_df.loc[:, "mean"], 'b', lw=2.5,marker='.',markersize=5)
    #ax.fill_between(obj_df.index, obj_df.loc[:, "mean"] - (1.96 * obj_df.loc[:, "std"]),
    #                obj_df.loc[:, "mean"] + (1.96 * obj_df.loc[:, "std"]),
    #                facecolor="b", edgecolor="none", alpha=0.25)
    axt.plot(obj_df.index,obj_df.loc[:,"lambda"],"k",dashes=(2,1),lw=2.5)
    ax.set_ylabel("log$_10$ phi")
    axt.set_ylabel("lambda")
    ax.set_title("total runs:{0}".format(obj_df.total_runs.max()))
    plt.savefig(os.path.join(plt_dir,"iobj.pdf"))
    plt.close()

    with PdfPages(os.path.join(plt_dir,"parensemble.pdf")) as pdf:

        for par_file,par_df in zip(par_files,par_dfs):
            print(par_file)
            fig = plt.figure(figsize=(20,10))

            plt.figtext(0.5,0.975,par_file,ha="center")
            axes = [plt.subplot(2,6,i+1) for i in range(len(par_names))]
            for par_name,ax in zip(par_names,axes):
                mean = par_df.loc[:,par_name].mean()
                std = par_df.loc[:,par_name].std()
                par_df.loc[:,par_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.5,grid=False)
                ax.set_yticklabels([])
                ax.set_title("{0}, {1:6.2f}".\
                             format(par_name,10.0**mean))
                ax.set_xlim(mn[par_name],mx[par_name])
                ylim = ax.get_ylim()
                if "stage" in par_name:
                    val = np.log10(1.5)
                else:
                    val = np.log10(2.5)
                ticks = ["{0:2.1f}".format(x) for x in 10.0**ax.get_xticks()]
                ax.set_xticklabels(ticks,rotation=90)
                ax.plot([val,val],ylim,"k-",lw=2.0)

                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
            pdf.savefig()
            plt.close()




    obs_files = [os.path.join(d,f) for f in os.listdir(d) if "obsensemble." in f
                 and ".png" not in f]
    obs_dfs = [pd.read_csv(obs_file) for obs_file in obs_files]
    #print(obs_files)
    #mx = max([obs_df.obs.max() for obs_df in obs_dfs])
    #mn = min([obs_df.obs.min() for obs_df in obs_dfs])
    #print(mn,mx)
    obs_names = ["h01_04","h01_06","h01_08","h02_08"]
    #print(obs_files)
    obs_dfs = [obs_df.loc[:,obs_names] for obs_df in obs_dfs]
    mx = {obs_name:max([obs_df.loc[:,obs_name].max() for obs_df in obs_dfs]) for obs_name in obs_names}
    mn = {obs_name:min([obs_df.loc[:,obs_name].min() for obs_df in obs_dfs]) for obs_name in obs_names}

    with PdfPages(os.path.join(plt_dir,"obsensemble.pdf")) as pdf:
        for obs_file,obs_df in zip(obs_files,obs_dfs):
            fig = plt.figure(figsize=(10,10))
            plt.figtext(0.5,0.975,obs_file,ha="center")
            print(obs_file)
            axes = [plt.subplot(2,2,i+1) for i in range(len(obs_names))]
            for ax,obs_name in zip(axes,obs_names):
                mean = obs_df.loc[:,obs_name].mean()
                std = obs_df.loc[:,obs_name].std()
                obs_df.loc[:,obs_name].hist(ax=ax,edgecolor="none",
                                            alpha=0.5,grid=False)
                ax.set_yticklabels([])
                #print(ax.get_xlim(),mn[obs_name],mx[obs_name])
                ax.set_title("{0}, {1:6.2f}:{2:6.2f}".format(obs_name,mean,std))
                #ax.set_xlim(mn[obs_name],mx[obs_name])
                ax.set_xlim(0.0,20.0)
                ylim = ax.get_ylim()
                oval = pst.observation_data.loc[obs_name,"obsval"]
                ax.plot([oval,oval],ylim,"k-",lw=2)
                ax.plot([mean,mean],ylim,"b-",lw=1.5)
                ax.plot([mean+(2.0*std),mean+(2.0*std)],ylim,"b--",lw=1.5)
                ax.plot([mean-(2.0*std),mean-(2.0*std)],ylim,"b--",lw=1.5)
            pdf.savefig()
            plt.close()



if __name__ == "__main__":
    #henry_setup()
    henry()
    henry_plot()
    #freyberg()
    #freyberg_plot()
    #chenoliver_setup()
    #chenoliver()
    #chenoliver_plot()
    #tenpar()
    #tenpar_plot()
