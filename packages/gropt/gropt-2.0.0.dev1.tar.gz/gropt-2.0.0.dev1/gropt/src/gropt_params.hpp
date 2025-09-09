#ifndef GROPT_PARAMS_H
#define GROPT_PARAMS_H

#include <iostream> 
#include <string>
#include <vector>
#include "Eigen/Dense"

#include "op_main.hpp"

namespace Gropt {

enum SolverMethod {
  GROPT_SDMM,
}; 

enum ILSMethod {
  CG,
  NLCG,
  BiCGstabl,
}; 

class SolverGroptSDMM;  // Forward declaration of SolverGroptSDMM class
class Operator;  // Forward declaration of Operator class
class GroptParams
{

    public:
        double dt = 10e-6;
        int N = 10;
        int Naxis = 1;
        // WARNING, TODO: Need to use getter and setters for N and Naxis to update Ntot automatically, it is not guaranteed now
        int Ntot = 10;  

        int vec_init_status = -1;
        int op_prep_status = -1;

        std::vector<Operator*> all_op;
        std::vector<Operator*> all_obj;

        Eigen::VectorXd X0;
        Eigen::VectorXd final_X;

        Eigen::VectorXd inv_vec;
        Eigen::VectorXd set_vals;
        Eigen::VectorXd fixer;

        ILSMethod ils_method = CG;
        SolverMethod solver_method = GROPT_SDMM;

        int iiter;
        int final_good = 0;
        int final_n_feval = 0;

        GroptParams();
        ~GroptParams() = default;

        void vec_init_simple(int _N, int _Naxis, double first_val, double last_val);
        void diff_init(double _dt, double _TE, double _T_90, double _T_180, double _T_readout);
        void setvec_X0(int _N, int _Naxis, double *_X0, bool set_others);

        void vec_reduce_simple(int N_reduce);

        void prepare();
        void warm_start_prev();

        void set_ils_solver(std::string ils_method);

        void add_gmax(double gmax, bool rot_variant, double weight_mod);
        void add_smax(double smax, bool rot_variant, double weight_mod);
        void add_moment(double order, double target, double tol0, std::string units,
                        int moment_axis, int start_idx0, int stop_idx0, int ref_idx0, double weight_mod);
        void add_SAFE(double stim_thresh,
                      double *tau1, double *tau2, double *tau3, 
                      double *a1, double *a2, double *a3,
                      double *stim_limit, double *g_scale,
                      int new_first_axis, bool demo_params, 
                      double weight_mod);
        void add_SAFE_vec(int N_vec, double *stim_thresh_vec,
                      double *tau1, double *tau2, double *tau3, 
                      double *a1, double *a2, double *a3,
                      double *stim_limit, double *g_scale,
                      int new_first_axis, bool demo_params, 
                      double weight_mod);

        void add_bvalue(double target, double tol, int start_idx0, int stop_idx0, double weight_mod);
        void add_TV(double tv_lam, double weight_mod);
        
        
        void add_obj_identity(double weight_mod);

        void solve();
        void solve(int min_iter, 
                   int n_iter, 
                   double gamma_x, 
                   double ils_tol, 
                   int ils_max_iter, 
                   int ils_min_iter, 
                   double ils_sigma,
                   double ils_tik_lam
                   );

        void test_reduce_and_solve();
        void test_reduce_and_solve(SolverGroptSDMM solver);

        void get_output(double **out, int &out_size);
};

Eigen::VectorXd linear_interpolate(const Eigen::VectorXd& in, int out_size);

} // namespace Gropt


#endif