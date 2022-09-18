# library of functions to get usage data stuff
from threading import local
import pandas as pd
import common
class MonthlyUsageData:

    def __init__(self,data):
        self.data = data


    def GetClientId(self):
        return self.data["client_id"]

    def GetMonth(self):
        return self.data["month"]

    def GetYear(self):
        return self.data["year"]


    def GetLocalCurrency(self):
        return self.data["client_config_used"]["local_ccy"]

    def GetPointValueInLocalCCY(self):
        return self.data["client_config_used"]["point_scheme"]["base_point_to_local_ccy_fx"]

    def GetTotalPointsAccrued(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["points"]

    def GetPointSTDConversionRatio(self):
        local_ccy = self.GetLocalCurrency()
        points_to_local_ratio = self.GetPointValueInLocalCCY()
        return points_to_local_ratio * common.STD_CCY_FX[local_ccy]

    def GetTotalPointsAccruedInSTD_CCY(self):
        return self.GetPointSTDConversionRatio() * self.GetTotalPointsAccrued()

    def GetTotalUsers(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["users"]

    def GetTotalActiveUsers(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["active_customers"]

    def GetTotalUsersWithPoints(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["users_with_points"]

    def GetPointsAccrued(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["points_accrued"]

    def GetPointsAccruedInSTD_CCY(self):
        return self.GetPointSTDConversionRatio() * self.GetPointsAccrued()

    def GetPointsRedeemed(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["points_redeemed"]

    def GetPointsRedeemedInSTD_CCY(self):
        return self.GetPointSTDConversionRatio() * self.GetPointsRedeemed()


    def GetActiveCustomers(self):
        return self.data["usage_metrics"]["lbms_usage_metrics"]["active_customers"]

    def GetMetricsDataFrame(self):

        accrual = self.GetPointsAccrued()
        redemption = self.GetPointsRedeemed()

        points_data = {"Points":[accrual,redemption]}
    # "Index":["Accrual", "Redemption"],
        df = pd.DataFrame(points_data, index=["Accrual", "Redemption"])

        return df

    def GetPointsAcrruedPerProduct(self):
        
        pointsDict = self.data["usage_metrics"]["lbms_usage_metrics"]["points_accrual_per_channel"]
        local_ccy = self.GetLocalCurrency()
        points_to_local_ratio = self.GetPointValueInLocalCCY()
        allProds = []
        accruals = []
        accrual_local_ccy = []
        accrual_std_ccy = []
        channels = []
        gmv = []
        expired = []
        gmv_std_ccy = []


        for channel in pointsDict.keys():
            for product in pointsDict[channel]:
                allProds.append(product["product_code"])
                accruals.append(int(product["accrued_on_period"]))
                accrual_local_ccy.append(int(points_to_local_ratio*product["accrued_on_period"]))
                #accrual_std_ccy.append("{:,.0f}".format(points_to_local_ratio*common.STD_CCY_FX[local_ccy]*product["accrued_on_period"]))
                accrual_std_ccy.append(int(points_to_local_ratio*common.STD_CCY_FX[local_ccy]*product["accrued_on_period"]))
                channels.append(channel)
                gmv.append(int(product["gmv_on_period"]))
                gmv_std_ccy.append(int(common.STD_CCY_FX[local_ccy]*product["gmv_on_period"]))
                expired.append(product["expired_on_period"])



        data = {"Product":allProds,
        "Channel":channels,
        "Points accrued":accruals,
        "Accrual in ST$":accrual_std_ccy,
        "Accrual in "+local_ccy:accrual_local_ccy ,
        "GMV in "+local_ccy:gmv,
        "GMV in ST$":gmv_std_ccy,
        "Points expired":expired}

        df = pd.DataFrame(data, 
        columns=["Product","Channel","Points accrued","Accrual in ST$", "Accrual in "+local_ccy, "GMV in ST$","GMV in "+local_ccy,"Points expired"],
        index=allProds)

        return df

    def GetPointsAcrruedPerChannel(self):
        
        pointsDict = self.data["usage_metrics"]["lbms_usage_metrics"]["points_accrual_per_channel"]
        local_ccy = self.GetLocalCurrency()
        points_to_local_ratio = self.GetPointValueInLocalCCY()
        accruals = []
        accrual_local_ccy = []
        accrual_std_ccy = []
        channels = []
        gmv = []
        expired = []
        gmv_std_ccy = []
        nb_prods = []

        channels =[]


        for channel in pointsDict.keys():
            channels.append(channel)
            nb_prod =0
            c_accruals = 0
            c_gmv = 0
            c_expired = 0
            for product in pointsDict[channel]:

                c_accruals += product["accrued_on_period"]
                c_gmv += product["gmv_on_period"]
                c_expired += product["expired_on_period"]
                nb_prod+=1

            nb_prods.append(nb_prod)
            accruals.append(c_accruals)
            accrual_local_ccy.append(int(points_to_local_ratio*c_accruals))
            accrual_std_ccy.append(int(points_to_local_ratio*common.STD_CCY_FX[local_ccy]*c_accruals))

            gmv.append(c_gmv)
            gmv_std_ccy.append(common.STD_CCY_FX[local_ccy]*c_gmv)

            expired.append(c_expired)

        data = {
        "Channel":channels,
        "Points accrued":accruals,
        "Accrual in ST$":accrual_std_ccy,
        "Accrual in "+local_ccy:accrual_local_ccy ,
        "GMV in "+local_ccy:gmv,
        "GMV in ST$":gmv_std_ccy,
        "Points expired":expired,
        "Nb Prod":nb_prods}

        df = pd.DataFrame(data, 
        columns=["Channel","Points accrued","Accrual in ST$", "Accrual in "+local_ccy, "GMV in ST$","GMV in "+local_ccy,"Points expired","Nb Prod"],
        index=channels)

        return df


    def GetRedemptionDataFrame(self):

        red_data = self.data["usage_metrics"]["lbms_usage_metrics"]["points_redeemed_per_redemption_option"]
        entryList = []
        spends ={}
        for opt in red_data.keys():
            if opt == "gift_card":
                common.AddToDic(spends,"Gift Cards",red_data[opt])
            elif opt=="utility":
                common.AddToDic(spends,"Utility",red_data[opt])
            elif opt=="charity":
                common.AddToDic(spends,"Charity",red_data[opt])
            elif opt=="transfer":
                common.AddToDic(spends,"Transfer",red_data[opt])
            elif opt=="miles_exchange":
                common.AddToDic(spends,"Points Exchange",red_data[opt])
            elif opt=="shop":
                common.AddToDic(spends,"E-Shop",red_data[opt])
            elif opt=="flight":
                common.AddToDic(spends,"Travel",red_data[opt])
                common.AddToDic(spends,"Travel/Flight",red_data[opt])
            elif opt=="hotel":
                common.AddToDic(spends,"Travel",red_data[opt])
                common.AddToDic(spends,"Travel/Hotel",red_data[opt])
            elif opt=="unknown_redemption_option":
                common.AddToDic(spends,"Unknown", red_data[opt])
            else:
                common.AddToDic(spends,"UNDEF/"+opt, red_data[opt])
                common.AddToDic(spends,"UNDEF", red_data[opt])
        
        # build the frame

        local_ccy = self.GetLocalCurrency()
        points_to_local_ratio = self.GetPointValueInLocalCCY()

        for entry in spends:
            entryList.append({"Classification":entry,"Points Redeemed":spends[entry],"#$ Redeemed":int(points_to_local_ratio*common.STD_CCY_FX[local_ccy]*spends[entry])})
        
        return pd.DataFrame(entryList)

    def GetUnitSTDDistribution(self):


        usersTiering = self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["users_points_tiering"]
        pointsTiering = self.data["usage_metrics"]["lbms_usage_metrics"]["lbms_state"]["points_points_tiering"]
        local_ccy = self.GetLocalCurrency()
        points_to_local_ratio = self.GetPointValueInLocalCCY()
        pointsToSTD = points_to_local_ratio*common.STD_CCY_FX[local_ccy]
        cat = []
        num_users =[]
        num_stdPoints =[]
        for bound in usersTiering["bounds"]:
            cat.append(pointsToSTD*bound["up"])
            num_users.append(bound["amount"])
        
        for bound in pointsTiering["bounds"]:
            num_stdPoints.append(pointsToSTD*bound["amount"])
        
        cat.append(float('inf'))
        num_users.append(usersTiering["max_tier_amount"])
        num_stdPoints.append(pointsToSTD*pointsTiering["max_tier_amount"])

        data = {
            "Points Value":cat,
            "Users":num_users,
            "#$ Value of Points":num_stdPoints
        }
        df = pd.DataFrame(data,
             columns=["Points Value","Users", "#$ Value of Points",'Avg #$ Per User'],
        )
        # Calculate Average #$ Value per user
        # Drop rows with 0 users
        df = df[df["Users"]>0]
        try:
            df['Avg #$ Per User'] = df.apply(lambda row: row["#$ Value of Points"] / row["Users"], axis=1)
        except:
            return df
        return df

    def GetAllRevenues(self):

        revenueEntries = []

        ubrevList =  self.data["client_revenue"]["usage_based_revenues"]
        for rev in ubrevList:
            revenueEntries.append({"Type":"Usage Based","Label":rev["label"],"Base Amount":float(rev["amount"]),"Base CCY":rev["ccy"],"Net Offset":rev["net_offset"]})

        fixedrevList =  self.data["client_revenue"]["fixed_revenues"]
        for rev in fixedrevList:
            revenueEntries.append({"Type":"Fixed","Label":rev["label"],"Base Amount":float(rev["amount"]),"Base CCY":rev["ccy"],"Net Offset":rev["net_offset"]})


        revDF = pd.DataFrame(revenueEntries)
        
        # Calculate #$
        revDF["#$ Amount"] = revDF.apply(lambda row: row["Base Amount"]*common.STD_CCY_FX[row["Base CCY"]],axis=1)
        revDF["Net #$ Amount"] =revDF.apply(lambda row: row["#$ Amount"]*(1- row["Net Offset"]),axis=1)

        return revDF


    def GetNetRevenue(self):
        revDF = self.GetAllRevenues()
        net = revDF["Net #$ Amount"].sum()
        return net

# Key Account Indicators #




    def GetTakeRate(self):
        revDF = self.GetAllRevenues()
        net = revDF["Net #$ Amount"].sum()
        df_chan_acc = self.GetPointsAcrruedPerChannel()
        total_GMV = df_chan_acc["GMV in ST$"].sum()
        return net/total_GMV

    def GetNetRevenuePerActiveUser(self):
        revDF = self.GetAllRevenues()
        net = revDF["Net #$ Amount"].sum()
        active = self.GetActiveCustomers()
        return net/active

    def GetMAUOverTU(self):
        return self.GetActiveCustomers()/self.GetTotalUsers()