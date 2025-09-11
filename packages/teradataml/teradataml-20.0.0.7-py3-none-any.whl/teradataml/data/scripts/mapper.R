#!/usr/bin/Rscript

# Read input from STDIN (standard input)
input <- file("stdin", open = "r")
while (length(line <- readLines(input, n = 1)) > 0) {
  # Remove leading and trailing whitespace
  line <- trimws(line)
  # Split the line into words
  words <- unlist(strsplit(line, "\\s+"))
  # Increase counters
  for (word in words) {
    # Write the results to STDOUT (standard output);
    # what we output here will be the input for the
    # Reduce step, i.e., the input for reducer.py
    #
    # tab-delimited; the trivial word count is 1
    cat(paste(word,"\t","1\n"))
  }
}
close(input)