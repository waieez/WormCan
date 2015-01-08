package com.appspot.elixian;

import java.util.ArrayList;
import java.util.List;
import com.appspot.elixian.FinanceCalc;

public class JavaSpring {

	public static void main(String[] args) {
		
		//System.out.printf("%,.2f", FinanceCalc.guessSalary(-999999,999999));
		/*
		Person self = new Person(26, 45, 85, 50000, 2610, .025, .077, .057);
		self.retire();
		self.estimateSalary();
		
		
		
		List<Person> people = new ArrayList<>();

		for (int i = 0; i < 25; i += 5) {
			people.add(new Person(24, 70 - i, 75, 50000, 2820, .025, .077, .057));
		}

		for (Person person : people) {
			person.toString();
			person.retire();			
			person.estimateSalary(33300.,.11);
			System.out.println();
		}
		*/
		List<Person> people2 = new ArrayList<>();

		for (double i = 0; i < .005 * 10; i += .005) {
			people2.add(new Person(26, 50, 75, 50000, 2650, .02, .01 + i, .05));
		}

		for (Person person : people2) {
			// person.getInfo();
			person.retire();
			System.out.println();
		}
	}
}