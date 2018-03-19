class TestModels(object):
    class MagnitudeConversion(object):
        simple_assignment = """
        neuron BlockTest:
            state:
                milliVolt mV = 10V
                Volt V
                Integer integer
                String string
            end
            function take_mV(milliVolt mV):
                return
            end
            function take_mV_return_mV(milliVolt mV) mV:
                return milliVolt
            end
            function take_mV_return_V(milliVolt mV) V:
                return milliVolt
            end
            update:
                Integer = 1
                Integer = inf
                String = "testString"
                milliVolt = 10V
                milliVolt = 10V + 5mV + 20V + 1kV
                Volt += 1200mV
                take_mV(10V)
                milliVolt = take_mV_return_mV(10V)
            end
            input:
            end
            output: spike
        end"""