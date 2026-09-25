package recitation;

import soot.jimple.DefinitionStmt;
import soot.options.*;
import soot.Local;
import soot.Unit;
import soot.Value;
import soot.ValueBox;
import soot.toolkits.graph.*;
import soot.toolkits.scalar.*;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/**
  Analysis to collect variables being defined. 
  The abstract data flow value (sigma) is a set of variable names (strings).
  This is like reaching definitions, but without tracking where variables
  were defined. So, the flow functions only have a GEN and no KILL.
*/
public class IntraDefsAnalysis extends ForwardFlowAnalysis<Unit, Set<String>> {


    IntraDefsAnalysis(UnitGraph graph) {
        super(graph);
    }

    // Runs the analysis
    public void run() {
        this.doAnalysis();
    }

    /**
     * Run flow function for this unit
     *
     * @param inValue  The initial Sigma at this point
     * @param unit     The current Unit
     * @param outValue The updated Sigma after the flow function
     */
    @Override
    protected void flowThrough(Set<String> inValue, Unit stmt, Set<String> outValue) {
        // First copy the sigma-in to sigma-out as-is
        outValue.addAll(inValue);

        // Check if a variable is being defined
        if (stmt instanceof DefinitionStmt) {
            DefinitionStmt def = (DefinitionStmt) stmt;
            Value lhs = def.getLeftOp();
            if (lhs instanceof Local) {
                // Get name of local variable being defined

                String varName = ((Local) lhs).getName();
                int lineNo = stmt.getJavaSourceStartLineNumber();

                Set<String> killSet = kill(varName, inValue);
                Set<String> genSet = gen(varName, lineNo);

                outValue.removeAll(killSet);
                outValue.addAll(genSet);
            }
        }
    }

    /**
     * Initial flow information at the start of a method
     */
    @Override
    protected Set<String> entryInitialFlow() {
        return new HashSet<String>(); // empty set
    }

    /**
     * Initial flow information at each other program point
     */
    @Override
    protected Set<String> newInitialFlow() {
        return new HashSet<String>(); // empty set
    }

    /**
     * Join at a program point lifted to sets
     */
    @Override
    protected void merge(Set<String> in1, Set<String> in2, Set<String> out) {
        // out := in1 union in2
        out.addAll(in1);
        out.addAll(in2);
    }

    private Set<String> kill(String varname, Set<String> sigma) {
        Set<String> results = new HashSet<String>();
        for (String element : sigma) {
            String[] splitted = element.split("@");
            if (splitted[0].equals(varname)) {
                results.add(element);
            }
        }
        return results;
    }

    private Set<String> gen(String varname, int lineNo) {
        Set<String> results = new HashSet<String>();
        results.add(varname + "@L" + lineNo);
        return results;
    }

    /**
     * Copy for sets
     */
    @Override
    protected void copy(Set<String> source, Set<String> dest) {
        // dest := source
        dest.addAll(source);
    }
}