from dlubal.api import rfem, common
import google.protobuf.json_format as pbjson

# Connect to the RFEM application
with rfem.Application() as rfem_app:

    # Concrete Design Configuration
    steel_uls_config = rfem_app.get_object(
        obj=rfem.steel_design_objects.SteelDesignUlsConfiguration(no=1)
    )

    settings_ec3 = steel_uls_config.settings_ec3
    print(f"SETTINGS_EC3:\n{settings_ec3}")

    common.set_tree_value(
        tree=settings_ec3,
        path=["options",
                "options_elastic_design_root",
                    "options_elastic_design"
        ],
        value=False
    )

    standard_params_ec3 = steel_uls_config.standard_parameters_tree
    print(f"STANDARD_PARAMETERS:\n{standard_params_ec3}")

    common.set_tree_value(
        tree=standard_params_ec3,
        path=["stainless_steel_acc_to_en_1993_1_4",
                "5_ultimate_limit_state_uls",
                    "5_6_shear_resistance",
                        "eta"
        ],
        value=1.5
    )

    steel_uls_config.ClearField("user_defined_name_enabled")

    rfem_app.update_object(
        obj=steel_uls_config
    )
