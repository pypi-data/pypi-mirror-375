#!/usr/bin/env python3

import sys
sys.path.append("../../scilink")

import scilink

# Configure APIs
scilink.configure('google', 'AIzaSyCeWoJCJWbBO6TmPcs3AFE8ZfieZ5wrOiY')
scilink.configure('futurehouse', '+MZqvbTtjHVywIJ1GWJ8Zw.platformv01.eyJqdGkiOiI1MDZiZjI2OS0wNThmLTRjNDUtYmM1OC1iMDE2NjYyYTBjMGUiLCJzdWIiOiJuaUt3MDBwVk1nUmV4MDhocUg3RTBTRFVXQ3UyIiwiaWF0IjoxNzQ0NzM4OTA5fQ.9xtT+1ZfVaKWHQurUAV69viXqaTh7YSH9nmDZ0DjnQU')


# Define image and metadata
image_path = "data/nanoparticles.npy" # GO_cafm.tif, nanoparticles.npy
system_info_path = "data/nanoparticles.json" # GO_cafm.json, nanoparticles.json

if __name__ == "__main__":

    workflow = scilink.workflows.ExperimentNoveltyAssessment(
        data_type='microscopy',
        enable_human_feedback=True,
        dft_recommendations=True,
        measurement_recommendations=True
    )

    result_unified = workflow.run_complete_workflow(
        data_path=image_path,
        system_info=system_info_path
    )

    print("\n--- Workflow Summary ---")
    print(workflow.get_summary(result_unified))
