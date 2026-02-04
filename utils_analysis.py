import incense
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sb
import json
import os

def print_system(exp):
    # Get the GridOut object
    grid_out = exp.artifacts["get_system.py"].file
    print(grid_out)
    # Read the content from the GridOut object
    content = grid_out.read().decode('utf-8')
    
    # Print the content
    return content


def load_json_data(file_path):
    """Load data from a JSON file."""
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data

def write_json_data(file_path, data):
    """Write JSON file."""
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)

def plot_exp(experiment_ids, v0, v1, save_folder, save_name, ext, loader):
    # Initialize the global dictionary
    global_dict = {"npq": [],
                   "error": []}
    
    # Create a new figure for plotting
    plt.figure()
    plt.xlabel("time stamp")
    plt.ylabel("fluo")
    
    # Iterate over the experiment IDs
    for i in experiment_ids:
        # Load the experiment
        exp = loader.find_by_id(i)
        
        # Plot the metrics
        sb.lineplot(exp.metrics)
        
        # Extract fluorescence data
        fluo = exp.metrics['data']
        data_fit = exp.metrics['fit_data']
        
        # Calculate npq and append to the global dictionary
        global_dict["npq"].append((fluo[v0] - fluo[v1]) / fluo[v0])
        
        # Calculate error and append to the global dictionary
        global_dict['error'].append(np.mean((data_fit - fluo) ** 2))
        
        # Extract xopt values and append to the global dictionary
        xopt = exp.config["fit_result"]['xopt']
        for key in xopt.keys():
            try:
                global_dict[key].append(xopt[key])
            except KeyError:
                global_dict[key] = [xopt[key]]
    
    # Save the first plot
    plt.savefig(save_folder + save_name + ext)
    
    # Create a new figure for the scatter plot
    plt.figure()
    for key in xopt.keys():
        m = np.mean(global_dict[key])
        plt.scatter(global_dict['npq'], global_dict[key] / m, label=key + " - %0.2e"%m)
        #plt.ylim(-10, 10)
        plt.legend()
    
    # Save the scatter plot
    plt.savefig(save_folder + save_name + '_scatter' + ext)
    
    # Write data to JSON file
    write_json_data(save_folder + save_name + ".json", global_dict)


def plot_error_bars(json_files):
    """Fetch all JSON files and plot the error bars."""
    
    errors = []
    file_names = []
    for json_file in json_files:
        data = load_json_data(json_file)
        errors.append(data['error'])
        fname = os.path.split(json_file)[1]
        file_names.append([fname]*len(data["error"]))
    print(errors)
    # Plot the error bars
    plt.figure(figsize=(15, 6))
    sb.pointplot(x = np.concatenate(file_names), y =np.concatenate(errors), join=False)

    
    plt.xlabel("num_params")
    plt.ylabel("Error")
    plt.title("Error Bars for Experiments")
    plt.show()

