import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class Parser {

	public static void main(String[] args) {
		try {
			Scanner scanner = new Scanner(new File("./parser/myfile.txt"));
			while (scanner.hasNextLine()) {
				for (String s : scanner.nextLine().trim().split(" ")){
					System.out.println(s);
				};
			}
			scanner.close();
		} catch (FileNotFoundException e) {
			e.printStackTrace();
		}
	}

}
