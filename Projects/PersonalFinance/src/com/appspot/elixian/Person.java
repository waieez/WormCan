package com.appspot.elixian;

import com.appspot.elixian.FinanceCalc;
import java.util.Scanner;

public class Person {

	private String name;
	private int age;
	private int retire;
	private int death;
	private double income;
	private double expense;
	private double inflation;
	private double saveGrowth;
	private double retireGrowth;
	
	private double pmt;
	private double deductions;

	public Person() {

		boolean bool = true;

		do {
			try {
				Scanner input = new Scanner(System.in);
				System.out.println("Retirement Calculator\n");

				System.out.print("What is your name? ");
				name = input.next();

				System.out.print("What is your age? ");
				age = input.nextInt();

				System.out.print("How old will you be when you retire? ");
				retire = input.nextInt();
				
				System.out.print("What is your life expectancy? ");
				death = input.nextInt();

				System.out.print("What is your annual income? ");
				income = input.nextDouble();

				System.out.print("How much are your monthly expenses? ");
				expense = input.nextDouble() * 12;

				System.out.print("What is the inflation rate? ( % ) ");
				inflation = input.nextDouble() / 100;

				System.out.print("What is your porfolio's growth rate while saving for retirement? ( % ) ");
				saveGrowth = input.nextDouble() / 100;

				System.out.print("What is your porfolio's growth rate in retirement? ( % ) ");
				retireGrowth = input.nextDouble() / 100;

				input.close();

				bool = false;
			} catch (Exception e) {
				System.out
						.println("Oops! That input was invalid. Please try again.");
			}
		} while (bool);
	}

	public Person(int age, int retire, int death, double income, double expense,
			double inflation, double saveGrowth, double retireGrowth) {
		this.name = "John Doe";
		this.age = age;
		this.retire = retire;
		this.death = death;
		this.income = income;
		this.expense = expense * 12;
		this.inflation = inflation;
		this.saveGrowth = saveGrowth;
		this.retireGrowth = retireGrowth;
	}

	public double retire() {

		int work = retire - age;

		double fvExpense = FinanceCalc.FV(expense, inflation, work);
		double cost = FinanceCalc.retirementCost(fvExpense, inflation, retireGrowth, death-retire);
		double pvCost = FinanceCalc.PV(cost, saveGrowth, work);

		double pmt = FinanceCalc.annuityPMT(pvCost, saveGrowth, work);
		System.out.printf("This is how much it will cost you today to retire @ %d: %,.2f, %,.2f \n", retire, pvCost, cost);
		System.out.printf("This is how much you need to save every year in order to retire @ %d: %,.2f \n", retire, pmt);
		System.out.printf("Rate: %.2f%%, PMT: %.2f\n", saveGrowth*100, pmt);
		
		this.pmt = pmt;
		return pmt;
	}
	
	
	public void estimateSalary () {
		boolean bool = true;
		
		do {
			try {
				double otherTaxes = 0;
				
				Scanner input = new Scanner(System.in);
				System.out.println("Salary Calculator\n");	

				System.out.print("What is the amount of your deductions? ");
				this.deductions = input.nextDouble();
				
				System.out.print("What is the combined % for other taxes (FICA/State)? ");
				otherTaxes = input.nextDouble() / 100;
			
				input.close();

				bool = false;
				
				double netIncome = pmt+expense-deductions;
				double estSalary = FinanceCalc.guessSalary(netIncome, netIncome) + deductions;
				System.out.printf("Earnings required after taxes to meet retirement goals, %,.2f \n", pmt+expense);
				System.out.printf("Estimated required salary before FICA/State taxes %,.2f\n", estSalary);
				System.out.printf("Estimated required salary including FICA/State %,.2f\n", estSalary/(1-otherTaxes));
				
			} catch (Exception e) {
				System.out.println("Oops! That input was invalid. Please try again.");
			}
		} while (bool);
	}
	
	public void estimateSalary(double deductions, double otherTaxes){
		
		double netIncome = pmt+expense-deductions;
		double estSalary = FinanceCalc.guessSalary(netIncome, netIncome) + deductions;
		
		System.out.printf("Earnings required after taxes to meet retirement goals, %,.2f \n", pmt+expense);
		System.out.printf("Estimated required salary before FICA/State taxes %,.2f\n", estSalary);
		System.out.printf("Estimated required salary including FICA/State %,.2f\n", estSalary/(1-otherTaxes));
		
	}
	
	public void getInfo() {
		System.out.printf("%.2f%%\n", saveGrowth*100);
	}

	public String toString() {
		System.out.printf("Name: %s, Age: %d, Retire: %d, Death:%d, Income: %.2f, Expenses: %.2f, Inflation: %.2f, Growth: %.2f, %.2f \n",
				name, age, retire, death, income, expense, inflation, saveGrowth, retireGrowth);
		return "toString method incomplete";
	}

}