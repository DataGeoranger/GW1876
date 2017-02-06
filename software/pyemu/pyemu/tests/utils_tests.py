import os
if not os.path.exists("temp"):
    os.mkdir("temp")

def add_pi_obj_func_test():
    import os
    import pyemu

    pst = os.path.join("utils","dewater_pest.pst")
    pst = pyemu.optimization.add_pi_obj_func(pst,out_pst_name=os.path.join("utils","dewater_pest.piobj.pst"))
    print(pst.prior_information.loc["pi_obj_func","equation"])
    #pst._update_control_section()
    assert pst.control_data.nprior == 1


def fac2real_test():
    import os
    import numpy as np
    import pyemu
    # pp_file = os.path.join("utils","points1.dat")
    # factors_file = os.path.join("utils","factors1.dat")
    # pyemu.utils.gw_utils.fac2real(pp_file,factors_file,
    #                               out_file=os.path.join("utils","test.ref"))

    pp_file = os.path.join("utils", "points2.dat")
    factors_file = os.path.join("utils", "factors2.dat")
    pyemu.utils.gw_utils.fac2real(pp_file, factors_file,
                                  out_file=os.path.join("utils", "test.ref"))
    arr1 = np.loadtxt(os.path.join("utils","fac2real_points2.ref"))
    arr2 = np.loadtxt(os.path.join("utils","test.ref"))

    #print(np.nansum(np.abs(arr1-arr2)))
    #print(np.nanmax(np.abs(arr1-arr2)))
    assert np.nanmax(np.abs(arr1-arr2)) < 0.01

    # import matplotlib.pyplot as plt
    # diff = (arr1-arr2)/arr1 * 100.0
    # diff[np.isnan(arr1)] = np.nan
    # p = plt.imshow(diff,interpolation='n')
    # plt.colorbar(p)
    # plt.show()

def vario_test():
    import numpy as np
    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        h = v.h_function(np.array([0.0]))
        assert h == contribution
        h = v.h_function(np.array([a*1000]))
        assert h == 0.0

        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        print(v2.h_function(np.array([a])))


def aniso_test():

    import pyemu
    contribution = 0.1
    a = 2.0
    for const in [pyemu.utils.geostats.ExpVario,pyemu.utils.geostats.GauVario,
                  pyemu.utils.geostats.SphVario]:

        v = const(contribution,a)
        v2 = const(contribution,a,anisotropy=2.0,bearing=90.0)
        v3 = const(contribution,a,anisotropy=2.0,bearing=0.0)
        pt0 = (0,0)
        pt1 = (1,0)
        assert v.covariance(pt0,pt1) == v2.covariance(pt0,pt1)

        pt0 = (0,0)
        pt1 = (0,1)
        assert v.covariance(pt0,pt1) == v3.covariance(pt0,pt1)

def geostruct_test():
    import pyemu
    v1 = pyemu.utils.geostats.ExpVario(0.1,2.0)
    v2 = pyemu.utils.geostats.GauVario(0.1,2.0)
    v3 = pyemu.utils.geostats.SphVario(0.1,2.0)

    g = pyemu.utils.geostats.GeoStruct(0.2,[v1,v2,v3])
    pt0 = (0,0)
    pt1 = (0,0)
    print(g.covariance(pt0,pt1))
    assert g.covariance(pt0,pt1) == 0.5

    pt0 = (0,0)
    pt1 = (1.0e+10,0)
    assert g.covariance(pt0,pt1) == 0.2

def struct_file_test():
    import os
    import pyemu
    struct = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))[0]
    print(struct)
    pt0 = (0,0)
    pt1 = (0,0)
    assert struct.covariance(pt0,pt1) == struct.nugget + \
                                         struct.variograms[0].contribution


def covariance_matrix_test():
    import os
    import pandas as pd
    import pyemu

    pts = pd.read_csv(os.path.join("utils","points1.dat"),delim_whitespace=True,
                      header=None,names=["name","x","y"],usecols=[0,1,2])
    struct = pyemu.utils.geostats.read_struct_file(
            os.path.join("utils","struct.dat"))[0]
    struct.variograms[0].covariance_matrix(pts.x,pts.y,names=pts.name)

    print(struct.covariance_matrix(pts.x,pts.y,names=pts.name).x)


def setup_ppcov_simple():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.struct2.out"),'','']
    args3 = [pts_file,'0.0',str_file,"struct3",os.path.join("utils","ppcov.struct3.out"),'','']


    for args in [args1,args2,args3]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)



def ppcov_simple_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_test.dat")

    mat1_file = os.path.join("utils","ppcov.struct1.out")
    mat2_file = os.path.join("utils","ppcov.struct2.out")
    mat3_file = os.path.join("utils","ppcov.struct3.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)
    ppc_mat3 = pyemu.Cov.from_ascii(mat3_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2,struct3 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)
    print(struct3)

    for mat,struct in zip([ppc_mat1,ppc_mat2,ppc_mat3],[struct1,struct2,struct3]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        print(str_mat.row_names)
        delt = mat.x - str_mat.x
        assert np.abs(delt).max() < 1.0e-7

def setup_ppcov_complex():
    import os
    import platform

    exe_file = os.path.join("utils","ppcov.exe")
    print(platform.platform())
    if not os.path.exists(exe_file) or not platform.platform().lower().startswith("win"):
        print("can't run ppcov setup")
        return
    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    args1 = [pts_file,'0.0',str_file,"struct1",os.path.join("utils","ppcov.complex.struct1.out"),'','']
    args2 = [pts_file,'0.0',str_file,"struct2",os.path.join("utils","ppcov.complex.struct2.out"),'','']

    for args in [args1,args2]:
        in_file = os.path.join("utils","ppcov.in")
        with open(in_file,'w') as f:
            f.write('\n'.join(args))
        os.system(exe_file + '<' + in_file)



def ppcov_complex_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    pts_file = os.path.join("utils","points1_test.dat")
    str_file = os.path.join("utils","struct_complex.dat")

    mat1_file = os.path.join("utils","ppcov.complex.struct1.out")
    mat2_file = os.path.join("utils","ppcov.complex.struct2.out")

    ppc_mat1 = pyemu.Cov.from_ascii(mat1_file)
    ppc_mat2 = pyemu.Cov.from_ascii(mat2_file)

    pts = pd.read_csv(pts_file,header=None,names=["name","x","y"],usecols=[0,1,2],
                      delim_whitespace=True)

    struct1,struct2 = pyemu.utils.geostats.read_struct_file(str_file)
    print(struct1)
    print(struct2)

    for mat,struct in zip([ppc_mat1,ppc_mat2],[struct1,struct2]):

        str_mat = struct.covariance_matrix(x=pts.x,y=pts.y,names=pts.name)
        delt = mat.x - str_mat.x
        print(mat.x[:,0])
        print(str_mat.x[:,0])


        print(np.abs(delt).max())

        assert np.abs(delt).max() < 1.0e-7
        #break

def pp_to_tpl_test():
    import os
    import pyemu
    pp_file = os.path.join("utils","points1.dat")
    pp_df = pyemu.gw_utils.pilot_points_to_tpl(pp_file,name_prefix="test_")
    print(pp_df.columns)


def to_mps_test():
    import os
    import pyemu
    jco_file = os.path.join("utils","dewater_pest.jcb")
    jco = pyemu.Jco.from_binary(jco_file)
    #print(jco.x)
    pst = pyemu.Pst(jco_file.replace(".jcb",".pst"))
    #print(pst.nnz_obs_names)
    oc_dict = {oc:"l" for oc in pst.nnz_obs_names}
    obj_func = {name:1.0 for name in pst.par_names}

    #pyemu.optimization.to_mps(jco=jco_file)
    #pyemu.optimization.to_mps(jco=jco_file,obs_constraint_sense=oc_dict)
    #pyemu.optimization.to_mps(jco=jco_file,obj_func="h00_00")
    decision_var_names = pst.parameter_data.loc[pst.parameter_data.pargp=="q","parnme"].tolist()
    pyemu.optimization.to_mps(jco=jco_file,obj_func=obj_func,decision_var_names=decision_var_names,
                              risk=0.975)

def setup_pp_test():
    import os
    import pyemu
    try:
        import flopy
    except:
        return
    model_ws = os.path.join("..","..","examples","Freyberg","extra_crispy")
    ml = flopy.modflow.Modflow.load("freyberg.nam",model_ws=model_ws)

    pp_dir = os.path.join("utils")
    ml.export(os.path.join(pp_dir,"test_unrot_grid.shp"))

    par_info_unrot = pyemu.gw_utils.setup_pilotpoints_grid(ml,prefix_dict={0:["hk1_","sy1_","rch_"]},
                                                     every_n_cell=2,pp_dir=pp_dir,tpl_dir=pp_dir,
                                                     shapename=os.path.join(pp_dir,"test_unrot.shp"))

    ml.sr.rotation = 15
    ml.export(os.path.join(pp_dir,"test_rot_grid.shp"))
    #pyemu.gw_utils.setup_pilotpoints_grid(ml)

    par_info_rot = pyemu.gw_utils.setup_pilotpoints_grid(ml,every_n_cell=2, pp_dir=pp_dir, tpl_dir=pp_dir,
                                                     shapename=os.path.join(pp_dir, "test_rot.shp"))

    print(par_info_unrot.x)
    print(par_info_rot.x)


def read_hob_test():
    import os
    import pyemu
    hob_file = os.path.join("utils","HOB.txt")
    pyemu.gw_utils.modflow_hob_to_instruction_file(hob_file)


def read_pval_test():
    import os
    import pyemu
    pval_file = os.path.join("utils", "meras_trEnhance.pval")
    pyemu.gw_utils.modflow_pval_to_template_file(pval_file)


def pp_to_shapefile_test():
    import os
    import pyemu
    try:
        import shapefile
    except:
        print("no pyshp")
        return
    pp_file = os.path.join("utils","points1.dat")
    shp_file = pp_file+".shp"
    pyemu.gw_utils.write_pp_shapfile(pp_file)

def write_tpl_test():
    import os
    import pyemu
    tpl_file = os.path.join("utils","test_write.tpl")
    in_file = os.path.join("utils","tpl_test.dat")
    par_vals = {"q{0}".format(i+1):12345678.90123456 for i in range(7)}
    pyemu.pst_utils.write_to_template(par_vals,tpl_file,in_file)


def read_pestpp_runstorage_file_test():
    import os
    import pyemu
    rnj_file = os.path.join("utils","freyberg.rnj")
    #rnj_file = os.path.join("..", "..", "verification", "10par_xsec", "master_opt1","pest.rnj")
    p1,o1 = pyemu.helpers.read_pestpp_runstorage(rnj_file)
    p2,o2 = pyemu.helpers.read_pestpp_runstorage(rnj_file,9)
    diff = p1 - p2
    diff.sort_values("parval1",inplace=True)

def smp_to_ins_test():
    import os
    import pyemu
    smp = os.path.join("utils","TWDB_wells.smp")
    ins = os.path.join('temp',"test.ins")
    try:
        pyemu.pst_utils.smp_to_ins(smp,ins)
    except:
        pass
    else:
        raise Exception("should have failed")
    pyemu.pst_utils.smp_to_ins(smp,ins,True)

def master_and_slaves():
    import shutil
    import pyemu
    slave_dir = os.path.join("..","..","verification","10par_xsec","template_mac")
    master_dir = os.path.join("temp","master")
    assert os.path.exists(slave_dir)
    #pyemu.helpers.start_slaves(slave_dir,"pestpp","pest.pst",1,
    #                           slave_root="temp",master_dir=master_dir)

    #now try it from within the master dir
    base_cwd = os.getcwd()
    os.chdir(master_dir)
    pyemu.helpers.start_slaves(os.path.join("..","..",slave_dir),
                              "pestpp","pest.pst",3,
                              master_dir='.')
    os.chdir(base_cwd)


def pearson_regul_test():
    import os
    import numpy as np
    import pandas as pd
    from pyemu import Schur
    from pyemu.utils.helpers import first_order_pearson_tikhonov
    #w_dir = os.path.join("..","..","verification","10par_xsec","master_opt0")
    w_dir = "la"
    sc = Schur(jco=os.path.join(w_dir,"pest.jcb"))
    sc.pst.zero_order_tikhonov()
    first_order_pearson_tikhonov(sc.pst,sc.posterior_parameter,reset=False)
    print(sc.pst.prior_information)

if __name__ == "__main__":
    pearson_regul_test()
    #master_and_slaves()
    #smp_to_ins_test()
    #read_pestpp_runstorage_file_test()
    # write_tpl_test()
    #pp_to_shapefile_test()
    # read_pval_test()
    # read_hob_test()
    #setup_pp_test()
    # to_mps_test()
    # pp_to_tpl_test()
    # setup_ppcov_complex()
    # ppcov_complex_test()
    # setup_ppcov_simple()
    # ppcov_simple_test()
    # fac2real_test()
    # vario_test()
    # geostruct_test()
    # aniso_test()
    # struct_file_test()
    # covariance_matrix_test()
    #add_pi_obj_func_test()