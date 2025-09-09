#ifndef GROPT_UTILS_H
#define GROPT_UTILS_H

/**
 * In general this is just a place for random usages of the GrOpt
 * operators for applications that aren't actual optimization.
 * 
 * i.e. GIRF respone calculation or spectral calcs, or getting a 
 * PNS curve for a waveform
 */

#include <iostream> 
#include <string>
#include <vector>
#include "Eigen/Dense"

namespace Gropt {
    
void set_verbose(int level);
void get_SAFE(int N, int Naxis, double dt, double *G_in, 
              bool true_safe, int new_first_axis, bool demo_params,
              double *tau1, double *tau2, double *tau3,
              double *a1, double *a2, double *a3,
              double *stim_limit, double *g_scale,
              double **out, int &out_size);
              
}  // close "namespace Gropt"

#endif