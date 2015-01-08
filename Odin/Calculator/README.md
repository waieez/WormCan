Demo @ http://jsfiddle.net/8br7kfgm/6/

#To Do: 
* Implement keyboard inputs
* Implement a text field where users can enter the value they want
* Styling to make it look more like google's calculator
* Still need to be smart about clearing entries


#Features:
* Chaining - Consecutive presses of the same function (eg ++ works as intended)
* Overrideable Operators - Change to/from different operators before computation


#Tests

##Simple Chain
```
1 + 1 + = + => 4
1 - 1 = - = => -2
5 * 5 * = * => 625
625 / 5 = / = => 5
```
##Simple Alternate
###	add subtract
```
1 + - 1 = 0
1 - + 1 = 2
```
###	multiply divide
```
5 * / 5 = 1
5 / * 5 = 25
```
##Mixed
###	multiply add multiply subtract multiply
```
2 * 2 + 2 * 2 - 2 * 2 = 20
```
###	divide add divide subtract divide
```
20 / 2 + 2 / 2 - 2 / 2 = 2
```