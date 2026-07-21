// Sample vulnerable Java servlet code for scanner demo purposes.
import java.io.*;
import java.sql.*;
import javax.servlet.http.*;

public class VulnerableServlet extends HttpServlet {

    private static final String DB_PASSWORD = "Admin@12345"; // hardcoded credential

    protected void doGet(HttpServletRequest request, HttpServletResponse response)
            throws IOException {

        PrintWriter out = response.getWriter();

        // SQL Injection: user input concatenated into query
        String userId = request.getParameter("id");
        try {
            Connection conn = DriverManager.getConnection(
                    "jdbc:mysql://localhost:3306/app", "root", DB_PASSWORD);
            Statement stmt = conn.createStatement();
            String query = "SELECT * FROM accounts WHERE id = " + userId;
            ResultSet rs = stmt.executeQuery(query);
        } catch (SQLException e) {
            e.printStackTrace();
        }

        // Reflected XSS: user input written directly to response
        String comment = request.getParameter("comment");
        out.println("<div>You said: " + comment + "</div>");

        // Command Injection: user input passed to Runtime.exec
        String host = request.getParameter("host");
        try {
            Runtime.getRuntime().exec("ping -c 1 " + host);
        } catch (IOException e) {
            e.printStackTrace();
        }

        // Insecure Deserialization: untrusted stream deserialized directly
        try {
            ObjectInputStream ois = new ObjectInputStream(request.getInputStream());
            Object obj = ois.readObject();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
