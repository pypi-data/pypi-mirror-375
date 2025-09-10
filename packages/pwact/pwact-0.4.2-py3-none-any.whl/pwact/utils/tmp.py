from pwdata import Config
import os, sys, glob
import numpy as np

def count_pwdata(work_dir):
    
    dir_list = glob.glob(os.path.join(work_dir, "*"))
    res = []
    for dir in dir_list:
        # train
        train_num = np.load(os.path.join(dir, "train/energies.npy")).shape[0]
        res.append(train_num)

        if os.path.exists(os.path.join(dir, "valid/energies.npy")):
            test_num = np.load(os.path.join(dir, "valid/energies.npy")).shape[0]
            res.append(test_num)
            print("{} {} {}".format( dir, train_num, test_num))
        else:
            print("{} {}".format(dir, train_num))
    print(np.sum(res))

def count_outmlmd():
    work_dir = "/data/home/wuxingxing/datas/debugs/dengjiapei/run_iter/iter.0000/label/scf"
    mlmds = glob.glob(os.path.join(work_dir, "*/*/*/OUT.MLMD"))
    print(len(mlmds))

def save_mlmd():
    work_dir = "/data/home/wuxingxing/datas/debugs/dengjiapei/run_iter"
    data_list = glob.glob(os.path.join(work_dir, "iter.*/label/scf/*/*/*/OUT.MLMD"))
    datasets_path = "/data/home/wuxingxing/datas/debugs/dengjiapei/run_iter/mlmd_pwdata"
    # data_name = datasets_path
    image_data = None
    for data_path in data_list:
        if image_data is not None:
            tmp_config = Config("pwmat/movement", data_path)
            # if not isinstance(tmp_config, list):
            #     tmp_config = [tmp_config]
            image_data.images.extend(tmp_config.images)
        else:
            image_data = Config("pwmat/movement", data_path)
            
            if not isinstance(image_data.images, list):
                image_data.images = [image_data.images]
        
            # if not isinstance(image_data, list):
            #     image_data = [image_data]
    image_data.to(
                output_path=datasets_path,
                save_format="pwmlff/npy",
                train_ratio = 0.8, 
                train_data_path="train", 
                valid_data_path="valid", 
                random=True,
                seed = 2024, 
                retain_raw = False
                )
    print(len(image_data.images))

def find_outcar_files(directory):
    outcar_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'OUTCAR' or file == "REPORT":
                outcar_files.append(os.path.join(root, file))
            
            
    return outcar_files

def is_convergence(file_path, format):
    def _is_cvg_vasp(file_path:str):
        with open(file_path, 'r') as rf:
            outcar_contents = rf.readlines()
        nelm = None
        ediff = None
        for idx, ii in enumerate(outcar_contents):
            if 'NELM   =' in ii:
                nelm = int(ii.split()[2][:-1])
            if 'EDIFF = ' in ii:
                ediff = float(ii.split()[-1])
        
        with open(os.path.join(os.path.dirname(os.path.abspath(file_path)), "OSZICAR"), 'r') as rf:
            oszi_contents = rf.readlines()
        _split = oszi_contents[-2].split()
        real_nelm = int(_split[1])
        real_ediff1 = abs(float(_split[3]))
        real_ediff2 = abs(float(_split[4]))

        if real_nelm < nelm:
            return True
        elif real_ediff1 <= ediff and real_ediff2 <=ediff:
            return True
        else:
            False

    def _is_cvg_pwmat(file_path:str):
        with open(file_path, 'r') as rf:
            report_contents = rf.readlines()
        e_error   = None
        rho_error = None
        etot_idx = -1
        drho_idx = -1
        for idx, ii in enumerate(report_contents):
            if e_error is None and 'E_ERROR   =' in ii:
                e_error = abs(float(ii.split()[-1]))
            if rho_error is None and 'RHO_ERROR =' in ii:
                rho_error = abs(float(ii.split()[-1]))
            if 'E_tot(eV)            =' in ii:
                etot_idx = idx
            if 'dv_ave, drho_tot     =' in ii:
                drho_idx = idx
            if 'niter reached' in ii:
                break
            elif 'ending_scf_reason = tol' in ii:
                return True

        if e_error >= abs(float(report_contents[etot_idx].split()[-1])) or \
            rho_error >= abs(float(report_contents[drho_idx].split()[-1])):
            return True
        return False
        
    if format == "vasp":
        return _is_cvg_vasp(file_path)
    elif format == "pwmat":
        return _is_cvg_pwmat(file_path)
    elif format == "cp2k":
        return True

def check_convergence(file_path:list[str], format:str):
    cvg_files = []
    uncvg_files = []
    cvg_infos = ""
    cvg_detail_infos=""
    for file in file_path:
        if is_convergence(file, format):
            cvg_files.append(file)
        else:
            uncvg_files.append(file)
    
    cvg_infos += "Number of converged files: {}, number of non-converged files: {}".format(len(cvg_files), len(uncvg_files))
    cvg_detail_infos += cvg_infos
    cvg_detail_infos += "\nList of non-converged files:\n{}".format("\n".join(uncvg_files))
    return cvg_files, uncvg_files, cvg_infos, cvg_detail_infos
    
def cvt_config():
    pwdata = "/data/home/wuxingxing/datas/pwmat_mlff_workdir/auag/pwdata/Ag4Au44"
    image = Config.read(data_path=pwdata, format="pwmlff/npy")[0][0]
    image.to(data_path="/share/public/PWMLFF_test_data/pwact_examples/25-pwact-demo/structures/AuAg", data_name="ag4au44-atom.config", format="pwmat/config")

if __name__=="__main__":
    # count_pwdata(work_dir = "/data/home/wuxingxing/datas/debugs/dengjiapei/run_iter/mlmd_pwdata")
    # count_outmlmd()
    # save_mlmd()
    # cvt_config()
    os.chdir("/share/public/PWMLFF_test_data/pwact_examples/25-pwact-demo/si_pwmat/run_iter_lmps/iter.0000/temp_run_iter_work/02.label/scf")
    current_dir = os.getcwd()
    outcar_files = find_outcar_files(current_dir)
    cvg_files, uncvg_files, cvg_infos, cvg_detail_infos = check_convergence(outcar_files, "pwmat")
    print(cvg_detail_infos)
    print(cvg_infos)

    