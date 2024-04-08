package main

import (
	"flag"
	"fmt"
	"os"
)

func main() {

	input_file := os.Args[1:][0]
	output_file := os.Args[1:][1]

	file := flag.String("file", input_file, fmt.Sprintf("specify the mapping file you want to solve\n--file %s", input_file))

	flag.Parse()

	game := NewGame(*file)

	result := game.solve()

	result_file, err := os.Create(output_file)

	if err != nil {
		fmt.Println("Unable to create file:", err)
		os.Exit(1)
	}
	defer result_file.Close()

	for _, v := range result.Moves {
		result_file.WriteString(fmt.Sprintf("%s\n", v))
	}
}
