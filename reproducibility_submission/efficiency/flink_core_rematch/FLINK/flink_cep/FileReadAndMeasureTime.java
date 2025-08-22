import java.nio.file.Files;
import java.nio.file.Paths;
import java.io.IOException;
import java.util.List;

public class FileReadAndMeasureTime {
    public static void main(String[] args) {
        // Replace the string with the path to your file
        String filePath = "test.txt";
        
        // Measure the start time
        long startTime = System.nanoTime();
        
        try {
            // Read all lines from the file
            List<String> allLines = Files.readAllLines(Paths.get(filePath));
            
            // Print each line
            for (String line : allLines) {
                System.out.println(line);
            }
            
            // Measure the end time
            long endTime = System.nanoTime();
            
            // Calculate the duration and convert to milliseconds
            long duration = (endTime - startTime) / 1_000_000; // Convert from nanoseconds to milliseconds
            
            System.out.println("Reading and printing took: " + duration + " ms");
            
        } catch (IOException e) {
            System.err.println("An error occurred while reading the file.");
            e.printStackTrace();
        }
    }
}
