package main

import (
	"flag"
	"fmt"
	"time"
	"os"
)

func main() {

	filename = os.Args[1:]

	file := flag.String("file", filename, "specify the mapping file you want to solve\n--file 647.json")

	flag.Parse()

	startDate := time.Now()
	game := NewGame(*file)

	result := game.solve()
	endDate := time.Now()

	diff := endDate.Sub(startDate)

	result_file, err := os.Create("%s.txt", filename)
     
    if err != nil{
        fmt.Println("Unable to create file:", err) 
        os.Exit(1) 
    }
    defer file.Close() 
    file.WriteString(result.Bottles)
	// fmt.Printf("Solution: %v\nduration: %s\n", result.Bottles, diff.String())

	for _, v := range result.Moves {
		fmt.Println(v)
	}
}
