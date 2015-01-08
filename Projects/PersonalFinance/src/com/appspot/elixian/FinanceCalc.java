package com.appspot.elixian;
import java.lang.Math;

public class FinanceCalc {

	public static double PV(double FV, double RATE, double PERIOD) {
		return FV * Math.pow((1 + RATE), -PERIOD);
	}
	
	public static double FV(double PV, double RATE, double PERIOD) {
		return PV * Math.pow((1 + RATE), PERIOD);
	}
	
	public static double annuityPMT(double FV, double RATE, double PERIOD) {
		return -FV * (RATE / (Math.pow(1 + RATE, -PERIOD) - 1));
	}
	
	public static double retirementCost(double EXPENSE, double INFLATION, double GROWTH, double PERIOD) {
		double cost = 0;
		for (double i = 0; i < PERIOD + 1; i++ ) {
			cost += PV(FV(EXPENSE, INFLATION, i), GROWTH, i);
		}
		return cost;
	}
	
	public static double guessSalary(double guess, double netIncome) {
		double estNetIncome = fedTaxes(guess);
		double difference = estNetIncome - netIncome;
		//System.out.printf("%,.2f --> %,.2f - %,.2f = %,.2f\n\n", guess, estNetIncome, netIncome, difference);
		if (difference > 1 || difference < -1) {
			return guessSalary(guess-(difference*1.5),netIncome);
		} else {
			return guess;
		}
	}
	
	public static double fedTaxes(double AGI) {
		// eventually do a switch/case for filing status
		double[] taxBracket = {0, 8925, 36250, 87850, 183250, 398350, 400000, Math.pow(10,10)};
		double[] taxRate = {0, .10, .15, .25, .28, .33, .35, .396};
		
		double tax = 0;
		
		for(int i=1; i < taxBracket.length; i++) {
			double currBracket = taxBracket[i];
			double currTaxRate = taxRate[i];
			double prevBracket = taxBracket[i-1];
			
			if (AGI <= currBracket) {
				tax += (AGI - prevBracket) * currTaxRate;
				//System.out.printf("(%,.2f - %,.2f) * %,.2f = %,.2f\n", AGI, prevBracket, currTaxRate, (AGI - prevBracket) * currTaxRate);
				break;
			} else {
				//System.out.printf("%,.2f * %,.2f = %,.2f\n", currBracket, currTaxRate, currBracket * currTaxRate);
				tax += (currBracket-prevBracket) * currTaxRate;
			}
		}
		return AGI-tax;
	}
}