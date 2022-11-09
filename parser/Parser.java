import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class Parser {

	public static void main(String[] args) {
		try {
			Scanner scanner = new Scanner(new File("./parser/myfile.txt"));
			while (scanner.hasNextLine()) {
				scanner.nextLine().trim().split("/\s+/");
			}
			scanner.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}

}
