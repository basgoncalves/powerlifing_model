import numpy as np
from scipy.integrate import odeint
import opensim as osim
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Create muscle model and simulate
    muscle = osim.Millard2012EquilibriumMuscle('muscle')
    muscle.setMaxIsometricForce(1000)
    muscle.setOptimalFiberLength(0.1)
    muscle.setTendonSlackLength(0.05)
    muscle.setPennationAngleAtOptimalFiberLength(0.0)

    # Create a model and add the muscle
    model = osim.Model()
    body = osim.Body('body', 1.0, osim.Vec3(0, 0, 0), osim.Inertia(1, 1, 1))
    model.addBody(body)
    model.addForce(muscle)

    max_forces = [100, 500, 1000, 1500, 2000]  # Different force levels to simulate
    for force in max_forces:
        muscle.setMaxIsometricForce(force)

        # Simulate muscle activation and force generation
        time = np.linspace(0, 1, 100)  # Simulate for 1 second
        activations = np.ones_like(time) * 0.5  # Constant activation at 50%
        fiber_lengths = []
        tendon_strains = []

        for t in time:
            muscle.setActivation(activations[int(t * len(time))])
            model.realizeDynamics()
            fiber_length = muscle.getFiberLength()
            tendon_length = muscle.getTendonLength()
            tendon_strain = (tendon_length - muscle.getTendonSlackLength()) / muscle.getTendonSlackLength()

            fiber_lengths.append(fiber_length)
            tendon_strains.append(tendon_strain)

        # Plot results
        plt.figure(figsize=(12, 6))
        plt.subplot(2, 1, 1)
        plt.plot(time, fiber_lengths, label=f'Max Force: {force} N')
        plt.title('Muscle Fiber Length Over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Fiber Length (m)')
        plt.legend()
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(time, tendon_strains, label=f'Max Force: {force} N')
        plt.title('Tendon Strain Over Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Tendon Strain')
        plt.legend()
        plt.grid()

    plt.show()