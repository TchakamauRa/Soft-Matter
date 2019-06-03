import matplotlib.pyplot as plt

def lines_plotter(line_vec1, line_vec2, point_vecsx, point_vecsy, sanity_point_vec, coltext):
    for i in range(len(point_vecsx)):
        plt.plot(point_vecsx[i], point_vecsy[i], ls = '-', c=coltext[i])
    for i in range(len(line_vec1)):
        plt.axhline(line_vec1[i], ls = ':', c=coltext[i])
        plt.axhline(line_vec2[i], ls = ':', c=coltext[i])
    units = np.ones(len(sanity_point_vec))
    plt.plot(units,sanity_point_vec, 'o')
    
def normalize_markov_matrix(matrix):
    T_expected_narrow = matrix
    T_eb = np.vstack([T_expected_narrow[0], 
                             (T_expected_narrow[1] + T_expected_narrow[2]) , 
                             (T_expected_narrow[3] + T_expected_narrow[4])])
    T_expected_broad = np.column_stack([T_eb[:, 0], 
                                 (T_eb[:, 1]+ T_eb[:, 2]), 
                                 (T_eb[:, 3]+ T_eb[:, 4])])
    T_expected_broad_norm  = np.vstack([T_expected_broad[0]/np.sum(T_expected_broad[0]), 
                                  T_expected_broad[1]/np.sum(T_expected_broad[1]), 
                                  T_expected_broad[2]/np.sum(T_expected_broad[2])])
    T_expected_broad_norm = np.vstack([T_expected_broad[i]/np.sum(T_expected_broad[i]) for i in range(len(T_expected_broad))])
    norm_matrix = T_expected_broad_norm
    return norm_matrix

def unit_left_eigenvector(matrix):
    eigvals, eigvecs = np.linalg.eig(matrix.T)
    eig_one_index = [x for x in range(len(eigvals)) if math.isclose(eigvals[x], 1.0, abs_tol = .0001)][0]
    eigvec_one = eigvecs[:, eig_one_index]
    evec_one = eigvec_one*100 / np.sum(eigvec_one)
    return evec_one