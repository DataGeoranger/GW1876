import os
if not os.path.exists("temp"):
    os.mkdir("temp")


def from_io_with_inschek_test():
    import os
    from pyemu import Pst,pst_utils
    # creation functionality
    dir = os.path.join("..","..","verification","10par_xsec","template_mac")
    pst = Pst(os.path.join(dir,"pest.pst"))


    tpl_files = [os.path.join(dir,f) for f in pst.template_files]
    out_files = [os.path.join(dir,f) for f in pst.output_files]
    ins_files = [os.path.join(dir,f) for f in pst.instruction_files]
    in_files = [os.path.join(dir,f) for f in pst.input_files]


    new_pst = pst_utils.pst_from_io_files(tpl_files, in_files,
                                ins_files, out_files,
                                pst_filename=os.path.join("pst","test.pst"))
    print(new_pst.observation_data)
    return

def tpl_ins_test():
    import os
    from pyemu import Pst,pst_utils
    # creation functionality
    dir = os.path.join("..","..","verification","henry","misc")
    files = os.listdir(dir)
    tpl_files,ins_files = [],[]
    for f in files:
        if f.lower().endswith(".tpl") and "coarse" not in f:
            tpl_files.append(os.path.join(dir,f))
        if f.lower().endswith(".ins"):
            ins_files.append(os.path.join(dir,f))

    out_files = [f.replace(".ins",".junk") for f in ins_files]
    in_files = [f.replace(".tpl",".junk") for f in tpl_files]

    pst_utils.pst_from_io_files(tpl_files, in_files,
                                ins_files, out_files,
                                pst_filename=os.path.join("pst","test.pst"))
    return


def res_test():
    import os
    import numpy as np
    from pyemu import Pst,pst_utils
    # residual functionality testing
    pst_dir = os.path.join('..','tests',"pst")

    p = Pst(os.path.join(pst_dir,"pest.pst"))
    phi_comp = p.phi_components
    assert "regul_p" in phi_comp
    assert "regul_m" in phi_comp

    p.adjust_weights_resfile()

    d = np.abs(p.phi - p.nnz_obs)
    assert d < 1.0E-5
    p.adjust_weights(obsgrp_dict={"head": 50})
    assert np.abs(p.phi_components["head"] - 50) < 1.0e-6

    # get()
    new_p = p.get()
    new_p.prior_information = p.prior_information
    new_file = os.path.join(pst_dir, "new.pst")
    new_p.write(new_file)

    p_load = Pst(new_file,resfile=p.resfile)
    for gname in p.phi_components:
        d = np.abs(p.phi_components[gname] - p_load.phi_components[gname])
        assert d < 1.0e-5

def pst_manip_test():
    import os
    from pyemu import Pst
    pst_dir = os.path.join('..','tests',"pst")
    org_path = os.path.join(pst_dir,"pest.pst")
    new_path = os.path.join(pst_dir,"pest1.pst")
    pst = Pst(org_path)
    pst.control_data.pestmode = "regularisation"
    pst.write(new_path)
    pst = Pst(new_path)

    pst.write(new_path,update_regul=True)




def load_test():
    import os
    from pyemu import Pst,pst_utils
    pst_dir = os.path.join('..','tests',"pst")
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    # just testing all sorts of different pst files
    pst_files = os.listdir(pst_dir)
    exceptions = []
    load_fails = []
    for pst_file in pst_files:
        if pst_file.endswith(".pst"):
            print(pst_file)
            try:
                p = Pst(os.path.join(pst_dir,pst_file))
            except Exception as e:
                exceptions.append(pst_file + " read fail: " + str(e))
                load_fails.append(pst_file)
                continue
            out_name = os.path.join(temp_dir,pst_file)
           #p.write(out_name,update_regul=True)
            try:
                p.write(out_name,update_regul=True)
            except Exception as e:
                exceptions.append(pst_file + " write fail: " + str(e))
                continue
            try:
                p = Pst(out_name)
            except Exception as e:
                exceptions.append(pst_file + " reload fail: " + str(e))
                continue

    #with open("load_fails.txt",'w') as f:
    #    [f.write(pst_file+'\n') for pst_file in load_fails]
    if len(exceptions) > 0:
        raise Exception('\n'.join(exceptions))

def smp_test():
    import os
    from pyemu.pst.pst_utils import smp_to_dataframe,dataframe_to_smp,\
        parse_ins_file,smp_to_ins
    
    smp_filename = os.path.join("misc","gainloss.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df,smp_filename+".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename+".ins")
    print(len(obs_names))

    smp_filename = os.path.join("misc","sim_hds_v6.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df,smp_filename+".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename+".ins")
    print(len(obs_names))


def smp_dateparser_test():
    import os
    from pyemu.pst.pst_utils import smp_to_dataframe,dataframe_to_smp,\
        parse_ins_file,smp_to_ins

    smp_filename = os.path.join("misc","gainloss.smp")
    df = smp_to_dataframe(smp_filename,datetime_format= "%d/%m/%Y %H:%M:%S")
    print(df.dtypes)
    dataframe_to_smp(df,smp_filename+".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename+".ins")
    print(len(obs_names))

    smp_filename = os.path.join("misc","sim_hds_v6.smp")
    df = smp_to_dataframe(smp_filename)
    print(df.dtypes)
    dataframe_to_smp(df,smp_filename+".test")
    smp_to_ins(smp_filename)
    obs_names = parse_ins_file(smp_filename+".ins")
    print(len(obs_names))


def tied_test():
    import os
    import pyemu
    pst_dir = os.path.join('..','tests',"pst")
    pst = pyemu.Pst(os.path.join(pst_dir,"br_opt_no_zero_weighted.pst"))
    print(pst.tied_lines)
    pst.write(os.path.join(pst_dir,"pest_tied_tester_1.pst"))
    mc = pyemu.MonteCarlo(pst=pst)
    mc.draw(1)
    mc.write_psts(os.path.join(pst_dir,"tiedtest_"))

def derivative_increment_tests():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst","inctest.pst"))
    pst.calculate_pertubations()

def regul_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst","inctest.pst"))
    pst.zero_order_tikhonov()
    print(pst.prior_information)

def pestpp_args_test():
    import os
    import pyemu
    pst_dir = os.path.join('..','tests',"pst")
    pst = pyemu.Pst(os.path.join(pst_dir,"br_opt_no_zero_weighted.pst"))
    pst.pestpp_options["lambdas"] = "0.1,0.2,0.3"
    pst.write(os.path.join("temp","temp.pst"))
    pst = pyemu.Pst(os.path.join("temp","temp.pst"))
    print(pst.pestpp_options)


def reweight_test():
    import os
    import numpy as np
    from pyemu import Pst,pst_utils
    pst_dir = os.path.join('..','tests',"pst")
    p = Pst(os.path.join(pst_dir,"pest.pst"))
    obsgrp_dict = {"pred":1.0,"head":1.0,"conc":1.0}
    p.adjust_weights(obsgrp_dict=obsgrp_dict)
    assert np.abs(p.phi - 3.0) < 1.0e-5,p.phi

    obs = p.observation_data
    obs.loc[obs.obgnme=="pred","weight"] = 0.0
    assert np.abs(p.phi - 2.0) < 1.0e-5,p.phi

    obs_dict = {"pd_one":1.0,"pd_ten":1.0}
    p.adjust_weights(obs_dict=obs_dict)
    assert np.abs(p.phi - 4.0) < 1.0e-5,p.phi




if __name__ == "__main__":
    #regul_test()
    #derivative_increment_tests()
    #tied_test()
    #smp_test()
    #smp_dateparser_test()
    #pst_manip_test()
    #tpl_ins_test()
    #load_test()
    res_test()
    #smp_test()
    #from_io_with_inschek_test()
    #pestpp_args_test()
    #reweight_test()