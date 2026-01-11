# Transformer configuration
transformer_params = {'n_layers': 1,
                      'n_heads': 8,
                      'dropout_rate': 0.2,
                      'projection_dim': 1024}

# Clinical metadata
categorical_features = {
    'names': [
        'sex',
        'atrial_fibrillation',
        'hypertension',
        'diabetes',
        'hyperlipidemia',
        'anticoagulation',
        'lipid_lowering_drugs',
        'pais',
        'wake_up',
        'in_house',
        'referral',
    ],
    'categories': [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
}
continuous_features = [
    'center',
    'age',
    'glucose',
    'leucocytes',
    'crp',
    'inr',
    'onset_to_door',
    'alert_to_door',
    'nihss_at_admission',
    'mrs_at_admission',
    'mrs_premorbid',
    'door_to_imaging',
    'door_to_groin',
    'door_to_first_series',
    'time_of_intervention',
    'door_to_recanalization',
]
target_feature = {'name': ['mRs90_binary'], 'categories': [2]}  # mRs90_binary = 0-2 (good), 3-6 (severe)

# Training configuration
train_params = {'n_epochs': 100,
                'learning_rate': 0.001}

# Data generator parameters
params = {'imagePath': './datasets/',
          'dictFile': './datasets/patient_dictionary.pickle',
          'clinicalFile': './datasets/clinical_metadata.csv',  # PATIENT_ID column must exist
          'resultsPath': './results/',
          'dim': (512, 512, 16),
          'batch_size': 1,
          'timepoints': 32,
          'n_classes': 2,
          'features': [continuous_features, categorical_features['names']]}
