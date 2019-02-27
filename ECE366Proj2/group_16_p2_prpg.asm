##
  # Eric Zavala Bautista 
  # ECE 366 - Project 1
  # 
##
 
addi $8, $0, 65533					# current seed

addi $9, $0, 16						# number of seeds to be created 
add $12, $0, $0						# next memory address to be used to store seed
add $14,$0,$0						# counter for hamming weight

loop_seeds:
	add $11, $8, $0	 
	j hamming_weight				# calculate hamming weight of current seed
	return_one:				
	sw $8, 0x2010($12)				# store the current seed
	addi $9, $9, -1					# decrease seed counter 
	beq $9, $0, hamming_distance			# check if more seeds are needed
	add $12, $12, 4					# increase memory offset for the next seed to be stored
	# algorithm for multiplication is as follows:
	# a = operand, b = operand, c = result. c = a*b
	#while b ? 0
	#    if (b and 1) ? 0
	#        c = c + a
	#    left shift a by 1
	#    right shift b by 1
	# c contains the result of multiplication
	add $10, $8, $0					# operand b used in multiplication
	add $11, $0, $0					# result of multiplication c
	square:	 					
		andi $13, $10, 1			# result of b && 0x1
		beq $13, $0, skip			# if (b and 1) ? 0
		addu $11, $11, $8			# c ? c + a
		skip:
		sll $8, $8, 1				# left shift a by 1
		srl $10, $10, 1				# right shift b by 1
		bne $10, $0, square			# while b ? 0
	remove_bits:
		andi $11, $11, 0x55555555 		# remove the odd bits
		add $8, $0, $0				# result
		addi $16, $0, 1
		addi $22, $0, 1
		loop_remove:
		and $23, $22, $11
		beq $23, $0, onward
		or $8, $8, $16
		onward:
		sll $22, $22, 2
		sll $16, $16, 1
		bne $22, $0, loop_remove
		j loop_seeds		
						
hamming_weight:
	andi $13,$11,0x1				# check if the bit is set in LSB
	beq $13,$0,continue	
	addi $14,$14,1					# if the LSB is set add 1 to hamming weight	
	continue:	
		srl $11,$11,1				# shift number to the right 1
		bne $11,$0,hamming_weight		# if the number is not 0 recheck LSB	
	bne $9, $0, return_one
	bne $17, 64, return_two
	j return_three
										
hamming_distance:
	srl $14, $14, 4					# take average of hamming weight 
	sw $14, 0x2000($0)
	add $14, $0, $0					
	
	# $15 = seed1, $16 = counter for outer loop, $17 = counter for inner loop, $18 = seed to compare to seed1
	# $19 = store whether or not seed in inner loop is adjacent to outer loop seed, $20 = old total hamming distance
	# $22 = counter for total neighboring hamming distance, $14 = repurposed to total hamming distance
	add $16, $0, $0					# counter for outer loop 
	add $22, $0, $0					# counter for hamming distance - part ii
	add $23, $0, $0
	loop_HD_one:					# for outer loop, loop through every seed
		beq $16, 64, end 				
		lw $15, 0x2010($16)		
		add $23, $23, $15
		addi $17, $16, 4			# counter for inner loop. It starts at position after outer loop 
		addi $16, $16, 4
	loop_HD_two:
		beq $17, 64, loop_HD_one
		sub $19, $17, $16			# check if current seed in inner loop is adjacent to seed in outer loop
		bne $19, 0, neighbors_one		# if seeds are adjacent then their hamming distance will be stored 
		add $20, $14, $0			# in both the counter for neighboring hamming distance and total hamming distance
neighbors_one:	lw $18, 0x2010($17)			# load seeds to compare to seed in outer loop
		xor $11, $18, $15			# xor to find the differing bits 
		j hamming_weight 			# calculate hamming distance
		return_two:
		bne $19, 0, neighbors_two		 
		sub $21, $14, $20			# substract new total hamming distance with old total hamming distance to find
		add $22, $22, $21			# hamming distance of adjacent seeds
neighbors_two:	addi $17, $17, 4			
		j loop_HD_two		
end:	
	# finding the average hamming distance without using division
	addi $8, $0, 120				# number of pairs 
	add $10, $0, $0					# add counter
	add $11, $0, $0					# number of additions
	division:
		add $10, $10, $8			# keep adding 120 to $10 until it is > total hamming distance
		addi $11, $11, 1			# keep track of how many additions 
		slt $13, $14, $10			
		bne $13, 1, division
	addi $11, $11, -1				# substract 1 to get integer part of the division
	sw $11, 0x2008($0)
	

###Hamming distance of first and last seed ######################
###Could be optimized by using more branch statements above######
	add $20, $14, $0					#
	lw $10, 0x2010($0)					#
	lw $11, 0x2040($0)					#
	xor $11, $11, $10					#
	j hamming_weight					#	
	return_three:						#
	sub $21, $14, $20					#
	add $22, $22, $21					#
#################################################################
	srl $22, $22, 4					# finding average
	srl $23, $23, 4
	sw $22, 0x2004($0)
	sw $23, 0x200c($0)
	
	
	
	
	
	
	
	
	
	
	
