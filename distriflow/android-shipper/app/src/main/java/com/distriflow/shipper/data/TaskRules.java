package com.distriflow.shipper.data;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class TaskRules {
    private TaskRules() {}
    public static boolean canScan(String status, boolean accepted, boolean arrived) {
        return "ready_for_handover".equals(status) && accepted && arrived;
    }
    public static boolean canConfirm(String status, boolean accepted, boolean arrived, List<String> packages, Set<String> scanned) {
        return canScan(status, accepted, arrived) && !packages.isEmpty() && scanned.equals(new HashSet<>(packages));
    }
}
