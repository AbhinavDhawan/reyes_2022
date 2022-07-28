import os, sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
try:
    import lsqfit
    import gvar as gv
except:
    sys.exit('you must install lsqfit for this code to work\npip install lsqfit')

def polynomial(x,p):
    ''' x = independent parameters
        p = dictionary of coefficients, p_0, p_1, ...
        y = p_0 + p_1 * x + p_2 * x**2 + ...
    '''
    y = 0
    for k in p:
        n = int(k.split('_')[1])
        y += p[k] * x**n
    return y

def add_noise(x, mu=0., sig=1., Nsamp=100, seed=None):
    ''' add random noise for all points x
        mu    : mean of noise
        sig   : width of noise
        Nsamp : number of random samples
        seed  : seed the random number generator with an int
    '''
    np.random.seed(seed)
    noise = np.random.normal(loc=mu, scale=sig, size=(Nsamp, x.shape[0]))

    return noise


def main():
    parser = argparse.ArgumentParser(
        description='Perform sample linear regression')
    ''' data options '''
    parser.add_argument('--data_n',        type=int, default=1,
                        help=              'order of polynomial to generate data [%(default)s]')
    parser.add_argument('--seed',          type=int, default=None,
                        help=              'integer seed for numpy random number generator [%(default)s]')
    parser.add_argument('--mu',            type=float, default=0,
                        help=              'mean of random noise [%(default)s]')
    parser.add_argument('--sig',           type=float, default=1,
                        help=              'width of random noise [%(default)s]')
    parser.add_argument('--Nsamp',         type=int,   default=100,
                        help=              'Number of random samples for noise [%(default)s]')

    ''' fitting options '''
    parser.add_argument('--fit_n',         type=int, default=1,
                        help=              'order of polynomial to fit data [%(default)s]')
    parser.add_argument('--freq_fit',      default=True, action='store_false',
                        help=              'Perform numerical frequentist fit? [%(default)s]')
    parser.add_argument('--linear',        default=False, action='store_true',
                        help=              'use VarPro to do linear regression? [%(default)s]')

    ''' plotting options '''
    parser.add_argument('--show_plots',    default=True, action='store_false',
                        help=              'Show plots?  [%(default)s]')
    parser.add_argument('--interact',      default=False, action='store_true',
                        help=              'open IPython instance after to interact with results? [%(default)s]')


    args = parser.parse_args()
    print(args)

    p0 = {'p_0':1.5, 'p_1':-0.3, 'p_2':0.04}

    ''' select parameters to generate data '''
    p_data = {k:v for k,v in p0.items() if int(k.split('_')[1]) <= args.data_n}

    ''' generate noisy data '''
    x = np.arange(0,10.2,.2)
    y = polynomial(x,p_data)
    g_noise = add_noise(x, mu=args.mu, sig=args.sig, Nsamp=args.Nsamp, seed=args.seed)
    y_g = np.zeros_like(g_noise)
    for i,d in enumerate(y):
        y_g[:,i] = d + g_noise[:,i]
    y_gv = gv.dataset.avg_data(y_g)

    ''' do numerical fits '''
    p_fit = {k:v for k,v in p0.items() if int(k.split('_')[1]) <= args.fit_n}
    linear=[]
    if args.linear:
        linear = [k for k in p_fit]
    if args.freq_fit:
        print('---------------------------------------------------------------')
        print('       Frequentist Fit')
        print('---------------------------------------------------------------')
        freq_fit = lsqfit.nonlinear_fit(data=(x, y_gv), p0=p_fit, fcn=polynomial, linear=linear)
        print(freq_fit)

    if args.show_plots:
        plt.ion()
        fig = plt.figure()
        ax  = plt.axes([0.12,0.12, 0.87, 0.87])
        ''' plot fit result '''
        x_plot = np.arange(x[0],x[-1]+.1,.1)
        if args.freq_fit:
            y_freq = polynomial(x_plot, freq_fit.p)
            r  = np.array([k.mean for k in y_freq])
            dr = np.array([k.sdev for k in y_freq])
            ax.fill_between(x_plot, r-dr, r+dr, color='r', alpha=.4)

        ''' plot data '''
        m   = np.array([k.mean for k in y_gv])
        dm  = np.array([k.sdev for k in y_gv])
        ax.errorbar(x,m, yerr=dm,
                    linestyle='None', marker='s', mfc='None', color='k')

    if args.interact:
        import IPython; IPython.embed()
    if args.show_plots:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()
