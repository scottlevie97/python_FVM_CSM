import timeit
import math
import os
import sys
import warnings

import numpy as np
from matplotlib import pyplot as plt
from scipy import sparse
from scipy.sparse.linalg import spsolve

from A_matrix import A
from boundary_conditions import boundary_conditions_A, boundary_conditions_b, addBoundaryDisplacements
from setup import *

warnings.filterwarnings('ignore', '.*do not.*', )

recordResults = True
plotOngoingResiudalGraph = True

# How many iterations  ons between plotting residuals
sampleRate = 200

# Time loop
if recordResults:
    os.system("mkdir " + saveDirectory(nx, ny))


start = timeit.default_timer()

# Define momentum loop tolerance:
tolerance = 1e-6

# Only allow one time-step if non transient
# if not transient:

t = np.array([0, 1])

# Initialise U_previous
U_previous = U_new

for time in t:

    print("\nTime = " + str(round(time, 1)))

    # Reset iteration counter
    icorr = 1

    # Set number of maximu_m iterations for convergence
    maxcorr = 100000

    # Make directory for timestep
    if recordResults:
        os.system("mkdir " + saveDirectory(nx, ny) + "/" + str(round(time, 2)))

    # Initialise arrays for graphs
    residual_array = np.array([])
    residual_array_x = np.array([])
    residual_array_y = np.array([])

    moving_average_array = np.array([])
    moving_average_graph_array = np.array([])

    # Create A matrices:
    A_x = A("x").createMatrix()
    A_x = boundary_conditions_A(A_x, U_previous, U_old, U_old_old, "x")

    A_y = A("y").createMatrix()
    A_y = boundary_conditions_A(A_y, U_previous, U_old, U_old_old, "y")

    # plt.hlines(tolerance, 0, len(moving_average_graph_array)*10, color = "C1", label  = "Tolerance")
    plt.yscale("log")
    plt.xlabel("Iterations")
    plt.ylabel("Residual")

    # Momentum Loop
    while True:

        # Store solution for previous iteration
        U_previous = U_new*1

        # x-equation
        # Create b matrices
        b_x = boundary_conditions_b(b_x, U_previous, U_old, U_old_old, "x")

        # # Solve for u
        A_x = sparse.csr_matrix(A_x)
        u = spsolve(A_x, b_x)

        # Reshape u
        u = u[:, None].reshape(b_x.shape)

        # y-equation
        # Create b matrices
        b_y = boundary_conditions_b(b_y, U_previous, U_old, U_old_old, "y")

        # # Solve for v
        A_y = sparse.csr_matrix(A_y)
        v = spsolve(A_y, b_y)

        # Reshape v
        v = v[:, None].reshape(b_y.shape)

        # Update U_New with new u and v fields
        U_new = np.hstack((u, v))

        # Calculate the residual of each iteration
        SMALL = 1e-20
        normFactor = np.max(U_new) + SMALL
        residual = math.sqrt(np.mean((U_new - U_previous)**2))/normFactor

        #######

        residual_vector = np.hstack((b_x - A_x.dot(u), b_y - A_y.dot(v)))

        # plt.scatter(residual_vector[16, 0], icorr)
        # plt.scatter(residual_vector[16, 1], icorr)

        plt.plot(icorr, residual_vector[16, 0], '.', color="C0")
        plt.plot(icorr, residual_vector[16, 1], '.', color="C1")

    

        # l2_norm_x = np.linalg.norm(residual_vector[:,0])
        # l2_norm_y = np.linalg.norm(residual_vector[:,1])

        # N_x = len(residual_vector[:,0])
        # N_y = len(residual_vector[:,1])

        # residual_x = l2_norm_x/np.sqrt(N_x)
        # residual_y = l2_norm_x/np.sqrt(N_y)

#         Ax = A_x.dot(u)
#         u_mean = u*1
#         for i in range(0, len(u[:, 0])):
#             u_mean[i] = np.mean(u)

#         Ax_mean = A_x.dot(u_mean)

#         normFactor_x = np.sum(np.sqrt((Ax - Ax_mean)**2) +
#                               np.sqrt((b_x - Ax_mean)**2))

#         residual_vector_x = residual_vector[:, 0]
#         residual_x = np.sum(np.sqrt((b_x - Ax)**2))/normFactor

#         Ay = A_y.dot(v)
#         v_mean = v*1
#         for i in range(0, len(v[:, 0])):
#             v_mean[i] = np.mean(v)
#         Ay_mean = A_y.dot(v_mean)

#         normFactor_y = np.sum(np.sqrt((Ay - Ay_mean)**2) +
#                               np.sqrt((b_y - Ay_mean)**2))

#         # print(normFactor_y)
# j
#         residual_vector_y = residual_vector[:, 1]

#         residual_y = np.sum(np.sqrt((b_y - Ay)**2))/normFactor
#         # residual_y = np.sum(np.sqrt(residual_vector_y**2))/normFactor

        # normFactor = np.max(math.sqrt(residual_vector**2)) + SMALL

        # residual = math.sqrt(np.mean((residual_vector)**2))/normFactor
        # residual = math.sqrt(np.mean((U_new - U_previous)**2))/normFactor

        ##########

        # Append residual array with residual
        residual_array = np.append(residual_array, residual)
        # residual_array_x = np.append(residual_array_x, residual_x)
        # residual_array_y = np.append(residual_array_y, residual_y)

        # The following is for on-going convergence reports:
        # Print out residual every 100 iterations
        if icorr % 100 == 0:
            moving_average = np.mean(
                residual_array[len(residual_array)-100:len(residual_array)])
            moving_average_array = np.append(
                moving_average_array, moving_average)
            print("Iteration: {:01d},\t Residual = {:.20f},\t normFactor = {:.20f},\t Moving Average = {:.20f},\t Time = {:.5f}".format(
                icorr, residual, normFactor, moving_average, time))

        # print("Iteration: {:01d},\t Residual = {:.20f}".format(
        #     icorr, residual))

        # # Calculate moving average of residual
        # if icorr % 10 == 0:
        #     moving_average_graph = np.mean(
        #         residual_array[len(residual_array)-10:len(residual_array)])
        #     moving_average_graph_array = np.append(
        #         moving_average_graph_array, moving_average_graph)

        # # # Print residual progress every 500 iterations
        # if icorr % 50 == 0:
        #     plt.plot(np.arange(100, len(moving_average_graph_array)*10, 10),
        #              moving_average_graph_array[10:len(moving_average_graph_array)], label="Moving Average", color="C2")

        # if (icorr % 10 == 0) & (icorr > 10):
        #     plt.plot(np.arange(10, len(moving_average_graph_array)*10, 10),
        #              moving_average_graph_array[1:len(moving_average_graph_array)], color="C0",  label="Residual")

        # if (icorr % 100 == 0):
            # plt.plot(np.arange(0, len(residual_array_x)), residual_array_x)
            # plt.plot(np.arange(0, len(residual_array_y)), residual_array_y)
            # print("residual_x: " + str(residual_x))
            # print("residual_y: " + str(residual_y))

        # if icorr <= 10:
        #     plt.plot(np.arange(0, len(residual_array)),
        #              residual_array, color="C0",  label="Residual")
        # plt.plot(icorr, residual, '.', label = "Residual", color = "C0")
        
        # plt.plot(icorr, tolerance, '.', label="Tolerance", color="C1")
        # if icorr == 1:
        #     plt.legend()

        if plotOngoingResiudalGraph:
            if (icorr % sampleRate == 0):
                plt.draw()
                plt.pause(0.00001)

        # Convergence check
        if residual < tolerance:

            print("\nResiduals have converged:\n")
            print("Iteration: {:01d},\t Residual = {:.20f},\t normFactor = {:.20f},\t Moving Average = {:.20f},\t Time = {:.5f}".format(
                icorr, residual, normFactor, moving_average, time))

            break

        elif icorr > maxcorr:

            break

        # Increment iteration counter
        icorr = icorr + 1

    # Update displacement temporal fields
    U_old_old = U_old
    U_old = U_new

    #------------------#
    # Save displacement field
    if recordResults:
        saveArray(str(round(time, 2)) + "/U_fine_mesh", U_new)

        U_with_boundaries, V_with_boundaries = addBoundaryDisplacements(U_new)
        saveArray(str(round(time, 2)) +
                  "/U_with_boundaries", U_with_boundaries)
        saveArray(str(round(time, 2)) +
                  "/V_with_boundaries", V_with_boundaries)


stop = timeit.default_timer()

print('Run time: ', stop - start)

# sys.stdout.close()

sys.exit()