import mapnik

def test_logger_init():
    assert mapnik.severity_type.Debug ==  0
    assert mapnik.severity_type.Warn ==  1
    assert mapnik.severity_type.Error ==  2
    assert getattr(mapnik.severity_type, "None") ==  3
    default = mapnik.logger.get_severity()
    mapnik.logger.set_severity(mapnik.severity_type.Debug)
    assert mapnik.logger.get_severity() ==  mapnik.severity_type.Debug
    mapnik.logger.set_severity(default)
    assert mapnik.logger.get_severity() ==  default
