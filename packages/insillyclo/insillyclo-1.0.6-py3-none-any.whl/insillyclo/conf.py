import configparser
import pathlib
from pathlib import Path
from typing import List

INSILLYCLO_INI = "insillyclo.ini"


class InSillyCloConfigIO:
    __in_config_property = []
    __global_config = Path.home() / f".{INSILLYCLO_INI}"

    @classmethod
    def in_config_property_decorator(cls, func):
        InSillyCloConfigIO.__in_config_property.append(func.__name__)
        return func

    @classmethod
    def in_config_property(cls) -> List[str]:
        return list(cls.__in_config_property)

    @classmethod
    def read_config(cls, local_config_file: str | pathlib.Path):
        config = configparser.ConfigParser()
        for config_path in [
            cls.__global_config,
            local_config_file,
        ]:
            if config_path is None:
                continue
            config.read(config_path)
        try:
            dilution_settings = config['DILUTION']
        except KeyError:
            return
        for prop_name in cls.__in_config_property:
            try:
                yield prop_name, cls.float_or_none(dilution_settings[prop_name])
            except KeyError:
                pass

    @staticmethod
    def float_or_none(v: str):
        if str(v).lower() == 'none':
            return None
        return float(v)

    @classmethod
    def write_config(
        cls,
        config,
        global_config: bool = False,
        local_config: pathlib.Path = None,
    ):

        config_override = configparser.ConfigParser()
        if global_config:
            location = cls.__global_config
        else:
            location = local_config
        config_override.read(location)

        if config is None:
            config = InSillyCloConfig()

        try:
            dilution_settings = config_override['DILUTION']
        except KeyError:
            config_override['DILUTION'] = dict()
            dilution_settings = config_override['DILUTION']

        for prop_name in cls.__in_config_property:
            dilution_settings[prop_name] = str(config.__getattribute__(prop_name))
        with open(location, 'w') as configfile:
            config_override.write(configfile)


class InSillyCloConfig:
    __config_provider_cls = InSillyCloConfigIO

    def __init__(self, config_file: str | pathlib.Path | None = INSILLYCLO_INI):
        self.__default_mass_concentration = None
        self.__output_plasmid_expected_volume = 10.0
        self.__enzyme_and_buffer_volume = 2.0
        self.__minimal_puncture_volume = 0.0
        self.__puncture_volume_10x = 1.0
        self.__minimum_remaining_volume_in_dilution = 2.0
        self.__expected_concentration_in_output = 2.0
        self.__nb_digits_rounding = 3
        self.config_file = config_file
        if config_file is None:
            return
        for k, v in self.__config_provider_cls.read_config(config_file):
            self.__setattr__(f'_{self.__class__.__name__}__{k}', v)

    def save(self, global_config: bool = False):
        self.__config_provider_cls.write_config(
            config=self,
            global_config=global_config,
            local_config=self.config_file,
        )

    def read_config(self):
        for prop_name in self.__config_provider_cls.in_config_property():
            try:
                yield prop_name, self.__getattribute__(prop_name)
            except KeyError:
                pass

    def update_settings(self, setting_name, settings_value):
        assert (
            setting_name in self.__config_provider_cls.in_config_property()
        ), f"Cannot override settings {setting_name} as not listed in IO settings"
        self.__setattr__(f'_{self.__class__.__name__}__{setting_name}', settings_value)

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def default_mass_concentration(self) -> float | None:
        """
        The default mass concentration (ng/µL) for input plasmid
        :return:
        """
        return self.__default_mass_concentration

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def output_plasmid_expected_volume(self) -> float:
        """
        The default expected volume (µL) for an output plasmid produced
        :return:
        """
        return self.__output_plasmid_expected_volume

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def enzyme_and_buffer_volume(self) -> float:
        """
        The volume (µL) of enzyme and buffer that have to be in each output plasmid well as recommended by the kit
        :return:
        """
        return self.__enzyme_and_buffer_volume

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def minimal_puncture_volume(self) -> float:
        """
        The default minimal volume (µL) to be taken at any moment
        :return:
        """
        return self.__minimal_puncture_volume

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def puncture_volume_10x(self) -> float:
        """
        The default volume (µL) taken from the input plasmid to create the intermediate dilution,
        but also the volume of the 10x dilution to take in order to produce the output plasmid.
        Can be more, but always a multiple of this volume.
        :return:
        """
        return self.__puncture_volume_10x

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def minimum_remaining_volume_in_dilution(self) -> float:
        """
        The default minimum volume (µL) to be left in a wheel after using it for all output plasmids.
        :return:
        """
        return self.__minimum_remaining_volume_in_dilution

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def expected_concentration_in_output(self) -> float:
        """
        The default minimum concentration (femtomol/µL) to have in intermediate dilution or output plasmid.
        :return:
        """
        return self.__expected_concentration_in_output

    @property
    @InSillyCloConfigIO.in_config_property_decorator
    def nb_digits_rounding(self) -> int:
        """
        The default number of digit to keep after comma.
        :return:
        """
        return self.__nb_digits_rounding
