Q1. Why does the swap grid start as a copy of the current state, rather than being
filled with zeros? What would happen to a grain that does not move if G′ started empty?
Ans. This is because in the program we have written, we first check if movement is possible and then we find out where the material is going to go and then change the material in the target row. But theres no else block. For the cases where movement is not possible, the material stays at the same place and we aren't appending the values. Had we updated each and every cell into Gprime every tick, then Gprime could start as a fresh array with all zeroes without any issue. But this approach is just simpler - take Gprime as a copy of G and update only the cells where some change is there.

Q2. Remove the randomised column order and replace it with a fixed left-to-right
scan. Run the simulation for a few hundred ticks. What happens to the shape of a sand pile?
Why?
Ans. When I did this to observe what happens, this is what I saw - when the iteration goes from left to right then the pile has a bias towards the right and when the iteration goes from right to left, the pile has a bias towards the left.
This is because in case where two cells want to slide down to a single particular cell, whoever is checked first wins. So when we are going left to right, lets say theres two cells in the same row with a cell in between them. Now in case they wanted to slide diagonally, both of them can potentially slide to the cell between them in the next row. But since the one on the left side is processed first, if it picks to go the cell in between then the cell on the right is forced to go right as the left diagonal is already filled. This creates a rightward bias as the cells to the left are processed first, if they choose to go right, the ones on the right have no option but to keep going right. This can be avoided by using a random permutation of cells in a row to process the movement.


Assignment Report:

In this assignment I learnt how to implement cellular automata using python and pygame. 
I followed the assignment pdf to understand how the rule in update is formulated and was impressed to see how such a simple rule governs the whole sand/water falling phenomenon.

Initially I wrote the code for the simulation using double loops to iterate through each and every cell in the grid one by one. It worked well but it wasn't as smooth as I thought it would be. So after I was done with both sand and water using loops, I took the help of LLMs to help me change the whole program and use vectorised operations instead of looping. This was in the bonus section of the week1 assignment but I could not do it back then, but I'm glad I was able to implement them in this simulation. I learnt about vectors on the go as I had LLMs guiding me through this restructuring, I had never used numpy arrays before and had never performed such operations on them so the whole thing was completely new to me.
But I spent a lott of time understanding every single line of my program and I can explain what every line means and why it's there (you can test me in the interview =D ). This took me a while but now I have a decent understanding of how vectorised operations work (how much ever is used in my program, I can understand to that level) and how to use them instead of for loops and how useful and fast they are.
In this version, the simulation was superr smooth.
Also I have made a few commits for every feature I have added/changed.

For the bonus part for now I have only added smoke as it was pretty easy. Fire would need me to add some rules for the reaction part as well and I'm not able to make time for that as I have midsems coming up too and my prep is kinda horror rn. If I'm able to make the time then I'll definitely try it out as it seems like a fun interesting addition to the simulation.