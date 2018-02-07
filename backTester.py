import Queue as queue
from dataHandler import csvData
from strategyManager import strangleStrat
from portfolioManager import portfolio
from datetime import datetime
import pytz
import logging
"""
This file contains a basic strategy example, and can be though of 
as an end-to-end test of the whole Backtester project
In this example, we actually backtest a strategy and do not use
the suite for live trading
"""

class BackTestSession(object):
    """Class for holding all parameters of backtesting session"""

    def __init__(self):

        # Create queue to hold events (ticks, signals, etc.)
        self.eventQueue = queue.Queue()

        # Create CsvData class object
        dataProvider = 'iVolatility'
        directory = '/Users/msantoro/PycharmProjects/Backtester/marketData/iVolatility/SPX/SPX_2011_2017'
        filename = 'RawIV.csv'
        chunkSize = 10000
        self.dataHandler = csvData.CsvData(directory, filename, dataProvider, self.eventQueue, chunkSize)

        # Parameters for strangle strategy -- TODO: move params to file
        optCallDelta = 0.16
        maxCallDelta = 0.30
        optPutDelta = -0.16
        maxPutDelta = -0.30
        startTime = datetime.now(pytz.utc)
        buyOrSell = 'SELL' # 'BUY' OR 'SELL'
        underlying = 'SPX'
        orderQuantity = 1
        daysBeforeClose = 5
        optimalDTE = 45
        minimumDTE = 25
        minCredit = 0.5
        profitTargetPercent = 0.5
        maxBidAsk = 15 # A general rule of thumb is to take 0.001*underlyingPrice.  Set to 15 to mostly ignore field
        minDaysToEarnings = None
        minDaysSinceEarnings = None
        minIVR = None
        self.strategyManager = strangleStrat.StrangleStrat(self.eventQueue, optCallDelta, maxCallDelta, optPutDelta,
                                                           maxPutDelta, startTime, buyOrSell, underlying,
                                                           orderQuantity, daysBeforeClose, optimalDTE=optimalDTE,
                                                           minimumDTE=minimumDTE, minDaysToEarnings=minDaysToEarnings,
                                                           minCredit=minCredit, profitTargetPercent=profitTargetPercent,
                                                           maxBidAsk=maxBidAsk,
                                                           minDaysSinceEarnings=minDaysSinceEarnings, minIVR=minIVR)


        startingCapital = 1000000
        maxCapitalToUse = 0.5
        maxCapitalToUsePerTrade = 0.05
        self.portfolioManager = portfolio.Portfolio(startingCapital, maxCapitalToUse, maxCapitalToUsePerTrade)

def run(session):

    while (1):  #Infinite loop to keep processing items in queue
        try:
            event = session.eventQueue.get(False)
        except queue.Empty:
            #Get data for tick event
            session.dataHandler.getNextTick()
        else:
            if event is not None:
                if event.type == 'TICK':
                    #self.cur_time = event.time
                    session.strategyManager.checkForSignal(event)
                    session.portfolioManager.updatePortfolio(event)
                elif event.type == 'SIGNAL':
                    session.portfolioManager.onSignal(event)
                elif event.type == 'ORDER':
                    pass
                    #self.execution_handler.execute_order(event)
                elif event.type == 'FILL':
                    pass
                    #self.portfolio_handler.on_fill(event)
                else:
                    raise NotImplemented("Unsupported event.type '%s'" % event.type)

if __name__ == "__main__":

    # Set up logging for the session
    logging.basicConfig(filename='session.log', level=logging.DEBUG)

    #Create a session and configure the session
    session = BackTestSession()

    #Create a backtester run
    run(session)