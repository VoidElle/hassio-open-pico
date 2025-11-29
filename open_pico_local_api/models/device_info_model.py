from dataclasses import dataclass


@dataclass
class DeviceInfoModel:
    """Device identification and hardware info"""
    ip: str
    firmware_version: str  # fw_ver
    firmware_note: str  # fw_note
    version: int  # vr
    model: int  # modello
    base_top: int  # BaseTop
    grid_datamatrix: str  # Grd_DM
    config_mode: int  # config_mod
    slave_id: int  # id_slave
    name: str
    has_slave: int
    slave_bitmap: int  # bmp_slave

    @property
    def firmware_full(self) -> str:
        """Full firmware version string"""
        return f"{self.firmware_version} ({self.firmware_note})"

    @property
    def has_datamatrix(self) -> bool:
        """Check if device has valid datamatrix"""
        return self.grid_datamatrix != "NoDataMatrix!!"